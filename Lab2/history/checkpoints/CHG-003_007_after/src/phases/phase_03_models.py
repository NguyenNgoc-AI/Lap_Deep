"""Pretrained model construction, layer audit and real-batch preflight."""
import gc
import time
from pathlib import Path

import torch
from torch import nn
from torchvision.models import VGG11_Weights, DenseNet121_Weights, vgg11, densenet121

from src.common import ROOT, config, now, read_json, sha256, source_hashes, write_json
from src.phases.phase_02_data import download, loader, MANIFEST
from src.phases.phase_01_environment import digest

WEIGHTS = {'vgg11': VGG11_Weights.IMAGENET1K_V1,
           'densenet121': DenseNet121_Weights.IMAGENET1K_V1}
WEIGHT_DIR = ROOT / 'data/weights/checkpoints'
OUT = ROOT / 'outputs/models'


def download_weights():
    provenance = {}
    for name, weights in WEIGHTS.items():
        path = WEIGHT_DIR / weights.url.rsplit('/', 1)[1]
        download(weights.url, path)
        checksum = sha256(path)
        expected = path.stem.rsplit('-', 1)[1]
        if not checksum.startswith(expected):
            raise ValueError(f'Weight checksum failed: {path}')
        provenance[name] = {'enum': str(weights), 'url': weights.url,
                            'path': str(path), 'sha256': checksum, 'bytes': path.stat().st_size}
    write_json(OUT / 'weights.json', provenance)
    return provenance


def build(name, mode='transfer', seed=42):
    if name not in WEIGHTS or mode not in ('transfer', 'finetune'):
        raise ValueError((name, mode))
    torch.manual_seed(seed)
    torch.hub.set_dir(str(ROOT / 'data/weights'))
    model = (vgg11 if name == 'vgg11' else densenet121)(weights=WEIGHTS[name])
    model.requires_grad_(False)
    if name == 'vgg11':
        model.classifier[-1] = nn.Linear(model.classifier[-1].in_features, 6)
        if mode == 'finetune':
            model.features[16:].requires_grad_(True)
    else:
        model.classifier = nn.Linear(model.classifier.in_features, 6)
        if mode == 'finetune':
            model.features.denseblock4.requires_grad_(True)
            model.features.norm5.requires_grad_(True)
    model.eval()
    return model


def synchronize(device):
    if device == 'xpu':
        torch.xpu.synchronize()


def verify_gradients(model):
    if any(p.grad is None for p in model.parameters() if p.requires_grad):
        raise FloatingPointError('A trainable parameter has no gradient')
    gradients = [p.grad.detach().norm() for p in model.parameters()
                 if p.requires_grad and p.grad is not None]
    if not gradients or not torch.isfinite(torch.stack(gradients)).all().item():
        raise FloatingPointError('Missing or non-finite gradients')


def preflight(device):
    records = []
    for name in WEIGHTS:
        for mode in ('transfer', 'finetune'):
            model = build(name, mode).to(device)
            trainable = [n for n, p in model.named_parameters() if p.requires_grad]
            (OUT / f'{name}_{mode}_architecture.txt').write_text(str(model), encoding='utf-8')
            frozen_names = {n for n, p in model.named_parameters() if not p.requires_grad}
            frozen_names.update(n for n, _ in model.named_buffers())
            before = digest({n: v for n, v in model.state_dict().items() if n in frozen_names})
            head = model.classifier[-1] if name == 'vgg11' else model.classifier
            head_before = head.weight.detach().cpu().clone()
            optimizer = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=.001)
            for batch in (8, 16):
                images, labels = next(iter(loader('train', batch, torch.Generator().manual_seed(42))))
                images, labels = images.to(device), labels.to(device)
                timings = []
                for step in range(3):
                    synchronize(device)
                    start = time.perf_counter()
                    optimizer.zero_grad(set_to_none=True)
                    logits = model(images)
                    if logits.shape != (len(labels), 6):
                        raise ValueError('Bad model output shape')
                    loss = nn.functional.cross_entropy(logits, labels)
                    if not torch.isfinite(loss).item():
                        raise FloatingPointError('Non-finite preflight loss')
                    loss.backward()
                    verify_gradients(model)
                    optimizer.step()
                    synchronize(device)
                    if step:
                        timings.append(time.perf_counter() - start)
                with torch.no_grad():
                    vimages, vlabels = next(iter(loader('validation', batch)))
                    validation = model(vimages.to(device))
                    if validation.shape != (len(vlabels), 6) or validation.requires_grad:
                        raise ValueError('Validation contract failed')
                records.append({'model': name, 'mode': mode, 'batch': batch, 'device': device,
                                'trainable_names': trainable,
                                'parameters_total': sum(p.numel() for p in model.parameters()),
                                'parameters_trainable': sum(p.numel() for p in model.parameters() if p.requires_grad),
                                'mean_step_seconds': sum(timings) / len(timings)})
                print(f'Preflight {name} {mode} B{batch} {device}: {records[-1]["mean_step_seconds"]:.3f}s', flush=True)
            after = digest({n: v for n, v in model.state_dict().items() if n in frozen_names})
            if before != after or torch.equal(head_before, head.weight.detach().cpu()):
                raise ValueError('Frozen/updated parameter contract failed')
            del model, head, optimizer, images, labels, logits, loss, validation
            gc.collect()
            if device == 'xpu':
                torch.xpu.empty_cache()
    return records


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    if not MANIFEST.exists():
        raise FileNotFoundError('Run PHASE-02 first')
    download_weights()
    if (OUT / 'preflight.json').exists():
        previous = read_json(OUT / 'preflight.json')
        if (previous['status'] == 'PASSED' and previous['source_hashes'] == source_hashes()
                and previous['manifest_sha256'] == sha256(MANIFEST)):
            return previous
    device = config()['device']
    reason = None
    if device == 'xpu' and not torch.xpu.is_available():
        device, reason = 'cpu', 'XPU unavailable'
    try:
        records = preflight(device)
    except torch.OutOfMemoryError:
        raise
    except (RuntimeError, NotImplementedError) as error:
        if device != 'xpu':
            raise
        gc.collect()
        torch.xpu.empty_cache()
        reason, device = str(error), 'cpu'
        print(f'XPU preflight failed, checking CPU for entire experiment matrix: {reason}', flush=True)
        records = preflight(device)
    result = {'status': 'PASSED', 'time': now(), 'device': device, 'fallback_reason': reason,
              'manifest_sha256': sha256(MANIFEST), 'source_hashes': source_hashes(), 'records': records}
    write_json(OUT / 'preflight.json', result)
    return result


if __name__ == '__main__':
    import sys
    download_weights() if '--download-only' in sys.argv else run()
