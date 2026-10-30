"""Authorized continuation of R07: import epoch3 state and run epochs4–5."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
from src.common import read_json, write_json, sha256, now
from src.phases.phase_04_train import OUT, provenance, fingerprint, train_run
from src.phases.phase_02_data import RAW, Scenes


def run():
    original = read_json(OUT / 'R07/result.json')
    original_identity = read_json(OUT / 'R07/identity.json')
    inputs = provenance()
    if inputs != original_identity['inputs']:
        raise ValueError('Source/data/dependency identity changed since original R07')
    assert original['status'] == 'COMPLETED' and original['history'][-1]['epoch'] == 3
    for name, checksum in original['checkpoint_hashes'].items():
        assert sha256(OUT / 'R07' / name) == checksum
    for split in ('train', 'validation'):
        for row in Scenes(split).rows:
            assert sha256(RAW / row['relative_path']) == row['sha256'], row['relative_path']
    spec = {**original['spec'], 'id': 'R07_5epochs', 'epochs': 5}
    lineage = {'original_run': 'R07', 'original_fingerprint': original['fingerprint'],
               'resume_from_epoch': 3, 'added_epochs': [4, 5],
               'original_checkpoint_hashes': original['checkpoint_hashes'],
               'extension_script_sha256': sha256(__file__),
               'interpretation': 'Exploratory continuation after original test was viewed; no new test evaluation'}
    inputs = {**inputs, 'extension': lineage}
    parent = read_json(OUT / 'R02/result.json')
    identity = {'spec': spec, 'device': original['device'], 'inputs': inputs,
                'parent': {'id': parent['id'], 'checkpoint': sha256(OUT / 'R02/best.pt')}}
    run_hash = fingerprint(identity)
    directory = OUT / spec['id']
    if not directory.exists():
        directory.mkdir()
        for name in ('last.pt', 'best.pt'):
            checkpoint = torch.load(OUT / 'R07' / name, map_location='cpu', weights_only=False)
            assert checkpoint['fingerprint'] == original['fingerprint']
            # Only run-identification metadata changes; model, optimizer and RNG values are retained.
            checkpoint['fingerprint'] = run_hash
            checkpoint['spec'] = spec
            checkpoint['history'] = [{**row, 'id': spec['id']} for row in checkpoint['history']]
            checkpoint['best'] = {**checkpoint['best'], 'id': spec['id']}
            temporary = directory / (name + '.tmp')
            torch.save(checkpoint, temporary)
            temporary.replace(directory / name)
            del checkpoint
        write_json(directory / 'identity.json', {'fingerprint': run_hash, **identity})
        write_json(directory / 'import_lineage.json', {'created': now(), **lineage,
                   'imported_checkpoint_hashes': {name: sha256(directory/name) for name in ('best.pt','last.pt')}})
    elif not (directory / 'import_lineage.json').exists():
        raise ValueError('Incomplete checkpoint import; preserve directory and inspect before continuing')
    result = train_run(spec, original['device'], inputs, parent=parent)
    assert [r['epoch'] for r in result['history']] == [1, 2, 3, 4, 5]
    for old, new in zip(original['history'], result['history'][:3]):
        assert {k:v for k,v in old.items() if k != 'id'} == {k:v for k,v in new.items() if k != 'id'}
    write_json(directory / 'comparison.json', {
        'status': 'COMPLETED', 'original_best': original['best'], 'extended_best': result['best'],
        'minimum_val_loss': min(result['history'], key=lambda r: (r['val_loss'],r['epoch'])),
        'validation_accuracy_change': result['best']['val_accuracy'] - original['best']['val_accuracy'],
        'test_evaluated': False, 'lineage': lineage})
    print('EXTENSION COMPLETED', result['best'], flush=True)


if __name__ == '__main__':
    run()
