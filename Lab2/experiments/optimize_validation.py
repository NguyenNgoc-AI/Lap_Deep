import gc
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
from torch.utils.tensorboard import SummaryWriter
from src.common import read_json, write_json, sha256, now
from src.phases.phase_02_data import RAW, MANIFEST, Scenes, loader
from src.phases.phase_03_models import build
from src.phases.phase_01_environment import digest
from src.phases.phase_04_train import epoch, seed_all, rng_state, restore_rng, save_checkpoint, provenance, fingerprint

OUT = ROOT / 'outputs/optimization_v1'
PROTOCOL = {'seed': 42, 'batch': 8, 'lr': 3e-6, 'max_epochs': 5,
            'patience': 2, 'min_delta': 1e-4, 'parent': 'R02', 'model': 'vgg11',
            'mode': 'finetune', 'optimizer': 'AdamW', 'device': 'xpu',
            'selection': 'max accuracy subject to loss <= initial validation loss; tie loss then epoch',
            'test_evaluated': False, 'exploratory_after_original_test': True}


def accuracy_rank(row):
    return (-row['val_accuracy'], row['val_loss'], row['epoch'])


def selected_row(history):
    eligible = [r for r in history if r['val_loss'] <= history[0]['val_loss']]
    return min(eligible, key=accuracy_rank)


def stop_update(loss, reference, bad):
    return (loss, 0) if loss < reference - PROTOCOL['min_delta'] else (reference, bad + 1)


def frozen_digest(model):
    frozen = {n for n, p in model.named_parameters() if not p.requires_grad}
    frozen.update(n for n, _ in model.named_buffers())
    return digest({n: p for n, p in model.state_dict().items() if n in frozen})


def train(run_id, weight_decay, inputs):
    directory = OUT / run_id
    directory.mkdir(parents=True, exist_ok=True)
    identity = {'protocol': PROTOCOL, 'run': run_id, 'weight_decay': weight_decay, 'inputs': inputs}
    identity['fingerprint'] = fingerprint(identity)
    identity_path = directory / 'identity.json'
    if identity_path.exists():
        assert read_json(identity_path) == identity, 'Changed protocol/source: use a new run'
    else:
        assert not any(directory.iterdir()), 'Unidentified output directory'
        write_json(identity_path, identity)
    if (directory / 'result.json').exists():
        result = read_json(directory / 'result.json')
        assert result['fingerprint'] == identity['fingerprint']
        for name, checksum in result['checkpoint_hashes'].items():
            assert sha256(directory / name) == checksum
        return result
    seed_all(PROTOCOL['seed'])
    generator = torch.Generator().manual_seed(PROTOCOL['seed'])
    device = PROTOCOL['device']
    model = build('vgg11', 'finetune', PROTOCOL['seed']).to(device)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                 lr=PROTOCOL['lr'], weight_decay=weight_decay)
    train_loader = loader('train', PROTOCOL['batch'], generator)
    val_loader = loader('validation', PROTOCOL['batch'])
    last = directory / 'last.pt'
    if last.exists():
        saved = torch.load(last, map_location='cpu', weights_only=False)
        assert saved['fingerprint'] == identity['fingerprint']
        model.load_state_dict(saved['model'])
        optimizer.load_state_dict(saved['optimizer'])
        history, reference, bad = saved['history'], saved['stop_reference'], saved['bad_epochs']
        frozen_before = saved['frozen_digest']
        restore_rng(saved['rng'], generator)
        for name, row in [('best.pt', selected_row(history)),
                          ('loss_best.pt', min(history, key=lambda r: (r['val_loss'], r['epoch'])))]:
            if row['epoch'] == saved['epoch']:
                save_checkpoint(directory / name, saved)
            assert (directory / name).exists()
        del saved
    else:
        parent = torch.load(ROOT / 'outputs/experiments/R02/best.pt', map_location='cpu', weights_only=False)
        model.load_state_dict(parent['model'])
        del parent
        frozen_before = frozen_digest(model)
        val = epoch(model, val_loader, device)
        assert val['samples'] == 2798
        history = [{'epoch': 0, 'val_loss': val['loss'], 'val_accuracy': val['accuracy'],
                    'val_samples': val['samples'], 'val_seconds': val['seconds']}]
        reference, bad = val['loss'], 0
        saved = {'fingerprint': identity['fingerprint'], 'epoch': 0, 'history': history,
                 'model': {n: p.detach().cpu() for n, p in model.state_dict().items()},
                 'optimizer': optimizer.state_dict(), 'rng': rng_state(generator, device),
                 'stop_reference': reference, 'bad_epochs': bad, 'frozen_digest': frozen_before}
        for name in ('last.pt', 'best.pt', 'loss_best.pt'):
            save_checkpoint(directory / name, saved)
        del saved
        write_json(directory / 'history.json', history)
    write_json(directory / 'status.json', {'status': 'RUNNING', 'updated': now(), 'next_epoch': history[-1]['epoch'] + 1})
    with SummaryWriter(str(directory / 'tensorboard'), purge_step=0) as writer:
        for row in history:
            for k, v in row.items():
                if k.startswith(('train_', 'val_')) and k.endswith(('loss', 'accuracy')):
                    writer.add_scalar(k, v, row['epoch'])
        for number in range(history[-1]['epoch'] + 1, PROTOCOL['max_epochs'] + 1):
            if bad >= PROTOCOL['patience']:
                break
            print(f'{run_id}: epoch {number}/{PROTOCOL["max_epochs"]}, weight_decay={weight_decay}', flush=True)
            tr = epoch(model, train_loader, device, optimizer)
            val = epoch(model, val_loader, device)
            assert tr['samples'] == 11208 and val['samples'] == 2798
            row = {'epoch': number, **{f'train_{k}': v for k, v in tr.items()},
                   **{f'val_{k}': v for k, v in val.items()}}
            history.append(row)
            reference, bad = stop_update(val['loss'], reference, bad)
            saved = {'fingerprint': identity['fingerprint'], 'epoch': number, 'history': history,
                     'model': {n: p.detach().cpu() for n, p in model.state_dict().items()},
                     'optimizer': optimizer.state_dict(), 'rng': rng_state(generator, device),
                     'stop_reference': reference, 'bad_epochs': bad, 'frozen_digest': frozen_before}
            save_checkpoint(last, saved)
            if selected_row(history)['epoch'] == number:
                save_checkpoint(directory / 'best.pt', saved)
            if min(history, key=lambda r: (r['val_loss'], r['epoch']))['epoch'] == number:
                save_checkpoint(directory / 'loss_best.pt', saved)
            del saved
            write_json(directory / 'history.json', history)
            for k, v in row.items():
                if k.startswith(('train_', 'val_')) and k.endswith(('loss', 'accuracy')):
                    writer.add_scalar(k, v, number)
            writer.flush()
            print(f'{run_id}: epoch={number}, val_acc={val["accuracy"]:.6f}, val_loss={val["loss"]:.6f}, patience={bad}/2', flush=True)
            write_json(directory / 'status.json', {'status': 'RUNNING', 'updated': now(), 'last_epoch': number,
                                                  'bad_epochs': bad})
    assert frozen_digest(model) == frozen_before, 'Frozen parameters changed'
    result = {'status': 'COMPLETED', 'run': run_id, 'fingerprint': identity['fingerprint'],
              'protocol': PROTOCOL, 'weight_decay': weight_decay, 'history': history,
              'selected': selected_row(history), 'best_accuracy': min(history, key=accuracy_rank),
              'best_loss': min(history, key=lambda r: (r['val_loss'], r['epoch'])),
              'stop_reason': 'early_stopping' if bad >= PROTOCOL['patience'] else 'max_epochs',
              'finished': now(), 'test_evaluated': False,
              'checkpoint_hashes': {n: sha256(directory / n) for n in ('best.pt', 'loss_best.pt', 'last.pt')}}
    write_json(directory / 'result.json', result)
    write_json(directory / 'status.json', {'status': 'COMPLETED', 'updated': now()})
    del model, optimizer, train_loader, val_loader
    gc.collect()
    torch.xpu.empty_cache()
    return result


def self_test():
    history = [{'epoch': 0, 'val_loss': .25, 'val_accuracy': .90},
               {'epoch': 1, 'val_loss': .26, 'val_accuracy': .95},
               {'epoch': 2, 'val_loss': .24, 'val_accuracy': .92}]
    assert selected_row(history)['epoch'] == 2
    assert selected_row(history[:2])['epoch'] == 0
    ref, bad = stop_update(.26, .25, 0)
    assert (ref, bad) == (.25, 1)
    ref, bad = stop_update(.27, ref, bad)
    assert bad == PROTOCOL['patience']
    assert stop_update(.24, ref, bad) == (.24, 0)
    p = torch.nn.Parameter(torch.tensor([1.]))
    opt = torch.optim.AdamW([p], lr=3e-6, weight_decay=.01)
    (p ** 2).sum().backward()
    opt.step()
    state = opt.state_dict()
    q = torch.nn.Parameter(p.detach().clone())
    resumed = torch.optim.AdamW([q], lr=3e-6, weight_decay=.01)
    import copy
    resumed.load_state_dict(copy.deepcopy(state))
    for parameter, optimizer in [(p, opt), (q, resumed)]:
        optimizer.zero_grad()
        (parameter ** 2).sum().backward()
        optimizer.step()
    assert torch.equal(p, q)
    print('PASS: selection constraint, early stopping, AdamW state resume', flush=True)


def run():
    self_test()
    if '--self-test' in sys.argv:
        return
    assert torch.xpu.is_available(), 'XPU unavailable: no implicit CPU fallback'
    assert sha256(MANIFEST) == read_json(ROOT / 'outputs/data/audit.json')['manifest_sha256']
    for split in ('train', 'validation'):
        for row in Scenes(split).rows:
            assert sha256(RAW / row['relative_path']) == row['sha256']
    parent = ROOT / 'outputs/experiments/R02/best.pt'
    assert sha256(parent) == read_json(parent.parent / 'result.json')['checkpoint_hashes']['best.pt']
    inputs = {'provenance': provenance(), 'script_sha256': sha256(__file__), 'parent_sha256': sha256(parent)}
    results = [train(run_id, wd, inputs) for run_id, wd in [('R08', 0.), ('R09', .01)]]
    winner = min(results, key=lambda r: (*accuracy_rank(r['selected']), r['run']))
    write_json(OUT / 'summary.json', {'status': 'COMPLETED', 'protocol': PROTOCOL,
               'winner': winner['run'], 'selected': winner['selected'], 'test_evaluated': False,
               'results': results, 'finished': now()})
    print('OPTIMIZATION COMPLETED', winner['run'], winner['selected'], flush=True)


if __name__ == '__main__':
    run()
