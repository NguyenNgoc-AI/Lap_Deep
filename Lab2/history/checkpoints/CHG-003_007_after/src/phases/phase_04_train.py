"""Seven sequential experiments, validation-only selection and epoch-boundary resume."""
import gc
import hashlib
import importlib.metadata
import json
import os
import random
import time

import numpy as np
import torch
from torch.utils.tensorboard import SummaryWriter

from src.common import ROOT, config, now, read_json, sha256, source_hashes, write_json
from src.phases.phase_02_data import MANIFEST, loader
from src.phases.phase_03_models import build, synchronize, verify_gradients

OUT = ROOT / 'outputs/experiments'


def provenance():
    return {'sources': source_hashes(), 'config': sha256(ROOT / 'configs/experiments.json'),
            'manifest': sha256(MANIFEST), 'weights': read_json(ROOT / 'outputs/models/weights.json'),
            'requirements': sha256(ROOT / 'requirements.txt'),
            'packages': {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}}


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def rng_state(generator, device):
    return {'python': random.getstate(), 'numpy': np.random.get_state(),
            'torch': torch.get_rng_state(), 'loader': generator.get_state(),
            'xpu': torch.xpu.get_rng_state_all() if device == 'xpu' else None}


def restore_rng(state, generator):
    random.setstate(state['python'])
    np.random.set_state(state['numpy'])
    torch.set_rng_state(state['torch'])
    generator.set_state(state['loader'])
    if state['xpu'] is not None:
        torch.xpu.set_rng_state_all(state['xpu'])


def save_checkpoint(path, value):
    temporary = path.with_suffix('.tmp')
    torch.save(value, temporary)
    os.replace(temporary, path)


def score(row):
    return (-row['val_accuracy'], row['val_loss'], row['epoch'], row.get('id', ''))


def epoch(model, batches, device, optimizer=None):
    # Frozen dropout and BatchNorm statistics stay fixed in both phases.
    model.eval()
    total_loss, correct, count = 0.0, 0, 0
    synchronize(device)
    started = time.perf_counter()
    with torch.set_grad_enabled(optimizer is not None):
        for step, (images, labels) in enumerate(batches, 1):
            images, labels = images.to(device), labels.to(device)
            if optimizer is not None:
                optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = torch.nn.functional.cross_entropy(logits, labels)
            if not torch.isfinite(loss).item():
                raise FloatingPointError('Non-finite loss')
            if optimizer is not None:
                loss.backward()
                verify_gradients(model)
                optimizer.step()
            total_loss += loss.item() * len(labels)
            correct += (logits.argmax(1) == labels).sum().item()
            count += len(labels)
            if step % 200 == 0:
                print(f'  {"train" if optimizer else "val"} {step}/{len(batches)} batches, loss={total_loss/count:.4f}', flush=True)
    synchronize(device)
    if count == 0:
        raise ValueError('Empty epoch')
    return {'loss': total_loss / count, 'accuracy': correct / count, 'samples': count,
            'seconds': time.perf_counter() - started}


def train_run(spec, device, inputs, parent=None):
    directory = OUT / spec['id']
    directory.mkdir(parents=True, exist_ok=True)
    identity = {'spec': spec, 'device': device, 'inputs': inputs,
                'parent': None if parent is None else {'id': parent['id'], 'checkpoint': sha256(OUT / parent['id'] / 'best.pt')}}
    run_hash = fingerprint(identity)
    metadata = directory / 'identity.json'
    if metadata.exists() and read_json(metadata)['fingerprint'] != run_hash:
        raise ValueError(f'Stale experiment: {spec["id"]}; preserve it and create a reviewed new experiment')
    if not metadata.exists():
        if any(directory.iterdir()):
            raise ValueError(f'Unidentified existing output: {directory}')
        write_json(metadata, {'fingerprint': run_hash, **identity})
    result_file = directory / 'result.json'
    if result_file.exists():
        result = read_json(result_file)
        if result['fingerprint'] == run_hash and result['status'] == 'COMPLETED':
            for name in ('best.pt', 'last.pt'):
                if sha256(directory / name) != result['checkpoint_hashes'][name]:
                    raise ValueError(f'Checkpoint changed: {directory / name}')
            print(f'{spec["id"]}: verified completed run', flush=True)
            return result
    seed_all(config()['seed'])
    generator = torch.Generator().manual_seed(config()['seed'])
    model = build(spec['model'], spec['mode'], config()['seed']).to(device)
    optimizer = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=spec['lr'])
    history, best, start_epoch = [], None, 1
    last_path = directory / 'last.pt'
    if last_path.exists():
        checkpoint = torch.load(last_path, map_location='cpu', weights_only=False)
        if checkpoint['fingerprint'] != run_hash:
            raise ValueError('Resume fingerprint mismatch')
        model.load_state_dict(checkpoint['model'])
        optimizer.load_state_dict(checkpoint['optimizer'])
        history, best = checkpoint['history'], checkpoint['best']
        start_epoch = checkpoint['epoch'] + 1
        best_path = directory / 'best.pt'
        if best['epoch'] == checkpoint['epoch']:
            # Repair a crash between the atomic last.pt and best.pt writes.
            save_checkpoint(best_path, checkpoint)
        elif not best_path.exists():
            raise ValueError('Missing earlier best checkpoint')
        restore_rng(checkpoint['rng'], generator)
        del checkpoint
        print(f'{spec["id"]}: resume at epoch {start_epoch}', flush=True)
    elif parent is not None:
        checkpoint = torch.load(OUT / parent['id'] / 'best.pt', map_location='cpu', weights_only=False)
        model.load_state_dict(checkpoint['model'])
        del checkpoint
    train_batches = loader('train', spec['batch'], generator)
    val_batches = loader('validation', spec['batch'])
    write_json(directory / 'status.json', {'status': 'RUNNING', 'updated': now(), 'next_epoch': start_epoch})
    with SummaryWriter(str(directory / 'tensorboard'), purge_step=0 if start_epoch > 1 else None) as writer:
        # Checkpoint history is authoritative if interruption happened before log flushing.
        for row in history:
            for split, prefix in [('train', 'train'), ('validation', 'val')]:
                for metric in ('loss', 'accuracy', 'seconds'):
                    writer.add_scalar(f'{split}/{metric}', row[f'{prefix}_{metric}'], row['epoch'])
        for number in range(start_epoch, spec['epochs'] + 1):
            print(f'{spec["id"]} {spec["model"]} {spec["mode"]}: epoch {number}/{spec["epochs"]}', flush=True)
            train = epoch(model, train_batches, device, optimizer)
            val = epoch(model, val_batches, device)
            row = {'id': spec['id'], 'epoch': number, 'train_loss': train['loss'], 'train_accuracy': train['accuracy'],
                   'val_loss': val['loss'], 'val_accuracy': val['accuracy'], 'train_seconds': train['seconds'],
                   'val_seconds': val['seconds'], 'train_samples': train['samples'], 'val_samples': val['samples']}
            history.append(row)
            improved = best is None or score(row) < score(best)
            if improved:
                best = row
            checkpoint = {'fingerprint': run_hash, 'spec': spec, 'epoch': number,
                          'model': {n: p.detach().cpu() for n, p in model.state_dict().items()},
                          'optimizer': optimizer.state_dict(), 'history': history, 'best': best,
                          'rng': rng_state(generator, device)}
            save_checkpoint(last_path, checkpoint)
            if improved:
                save_checkpoint(directory / 'best.pt', checkpoint)
            del checkpoint
            write_json(directory / 'history.json', history)
            for split, values in [('train', train), ('validation', val)]:
                for metric in ('loss', 'accuracy', 'seconds'):
                    writer.add_scalar(f'{split}/{metric}', values[metric], number)
            writer.flush()
            print(f'{spec["id"]} epoch {number}: train={train["accuracy"]:.4f} val={val["accuracy"]:.4f} val_loss={val["loss"]:.4f}', flush=True)
            write_json(directory / 'status.json', {'status': 'RUNNING', 'updated': now(), 'next_epoch': number + 1})
    result = {'status': 'COMPLETED', 'id': spec['id'], 'spec': spec, 'device': device, 'best': best,
              'fingerprint': run_hash, 'finished': now(), 'history': history,
              'seconds': sum(r['train_seconds'] + r['val_seconds'] for r in history),
              'checkpoint_hashes': {n: sha256(directory / n) for n in ('best.pt', 'last.pt')}}
    write_json(result_file, result)
    write_json(directory / 'status.json', {'status': 'COMPLETED', 'updated': now()})
    del model, optimizer, train_batches, val_batches
    gc.collect()
    if device == 'xpu':
        torch.xpu.empty_cache()
    return result


def run():
    settings = config()
    preflight = read_json(ROOT / 'outputs/models/preflight.json')
    if preflight['status'] != 'PASSED' or preflight['manifest_sha256'] != sha256(MANIFEST):
        raise ValueError('Missing or stale preflight')
    if preflight['source_hashes'] != source_hashes():
        raise ValueError('Code changed since preflight; rerun PHASE-03')
    inputs = provenance()
    from src.phases.phase_02_data import RAW, Scenes
    for split in ('train', 'validation', 'test'):
        for row in Scenes(split).rows:
            if sha256(RAW / row['relative_path']) != row['sha256']:
                raise ValueError(f'Raw image changed: {row["relative_path"]}')
    device = preflight['device']
    results = [train_run(spec, device, inputs) for spec in settings['runs']]
    winner = min(results, key=lambda r: score(r['best']))
    fine_spec = {**settings['fine_tune'], 'model': winner['spec']['model'], 'batch': winner['spec']['batch']}
    write_json(OUT / 'transfer_selection.json', {'selected_before_test': now(), 'winner': winner['id'], 'rule': 'validation accuracy desc, loss asc, epoch asc, run ID asc'})
    results.append(train_run(fine_spec, device, inputs, parent=winner))
    selected = min(results, key=lambda r: score(r['best']))
    per_model = {name: min([r for r in results[:6] if r['spec']['model'] == name], key=lambda r: score(r['best']))['id']
                 for name in ('vgg11', 'densenet121')}
    selection = {'selected_before_test': now(), 'final_run': selected['id'], 'best_transfer': winner['id'],
                 'best_transfer_per_model': per_model, 'test_runs': list(per_model.values()) + ['R07'],
                 'rule': 'validation accuracy desc, loss asc, epoch asc, run ID asc', 'provenance_hash': fingerprint(inputs)}
    existing = OUT / 'selection.json'
    if existing.exists():
        previous = read_json(existing)
        if {k: v for k, v in previous.items() if k != 'selected_before_test'} != {k: v for k, v in selection.items() if k != 'selected_before_test'}:
            raise ValueError('Selection changed after being frozen')
        selection = previous
    else:
        write_json(existing, selection)
    return {'selection': selection, 'runs': results}


if __name__ == '__main__':
    run()
