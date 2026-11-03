from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import torch
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from src.common import read_json, sha256, write_json, now
from experiments.optimize_validation import selected_row, stop_update, PROTOCOL


def run():
    out = ROOT / 'outputs/optimization_v1'
    summary = read_json(out / 'summary.json')
    assert summary['status'] == 'COMPLETED' and not summary['test_evaluated']
    initial = None
    checks = []
    for result in summary['results']:
        directory = out / result['run']
        history = result['history']
        assert [r['epoch'] for r in history] == list(range(len(history)))
        assert len(history) <= PROTOCOL['max_epochs'] + 1
        assert result['selected'] == selected_row(history)
        value = (history[0]['val_loss'], history[0]['val_accuracy'])
        if initial is None:
            initial = value
        else:
            assert value == initial, 'Different initial metrics between controlled runs'
        reference, bad = history[0]['val_loss'], 0
        for row in history[1:]:
            assert bad < PROTOCOL['patience'], 'Run continued after stopping condition'
            assert row['train_samples'] == 11208 and row['val_samples'] == 2798
            reference, bad = stop_update(row['val_loss'], reference, bad)
        assert result['stop_reason'] == ('early_stopping' if bad >= PROTOCOL['patience'] else 'max_epochs')
        for name, expected in result['checkpoint_hashes'].items():
            assert sha256(directory / name) == expected
            checkpoint = torch.load(directory / name, map_location='cpu', weights_only=False)
            expected_epoch = (result['selected']['epoch'] if name == 'best.pt' else
                              result['best_loss']['epoch'] if name == 'loss_best.pt' else history[-1]['epoch'])
            assert checkpoint['epoch'] == expected_epoch
            assert checkpoint['fingerprint'] == result['fingerprint']
            del checkpoint
        accumulator = EventAccumulator(str(directory / 'tensorboard')).Reload()
        for key in ('train_loss', 'train_accuracy', 'val_loss', 'val_accuracy'):
            events = accumulator.Scalars(key)
            expected = [r for r in history if key in r]
            assert [e.step for e in events] == [r['epoch'] for r in expected]
            assert all(abs(e.value - r[key]) < 1e-6 for e, r in zip(events, expected))
        checks.append({'run': result['run'], 'epochs': len(history)-1, 'status': 'PASS'})
    original = read_json(ROOT / 'outputs/delivery_manifest.json')['files']
    for path, checksum in original.items():
        assert sha256(ROOT / path) == checksum, path
    identity = read_json(out / 'R08/identity.json')
    for path, checksum in identity['inputs']['provenance']['sources'].items():
        assert sha256(ROOT / path) == checksum, path
    verification = {'status': 'PASS', 'created': now(), 'runs': checks,
                    'original_artifacts_unchanged': len(original), 'source_unchanged': True,
                    'same_initial_metrics': True, 'test_evaluated': False}
    write_json(out / 'verification.json', verification)
    print(verification)


if __name__ == '__main__':
    run()
