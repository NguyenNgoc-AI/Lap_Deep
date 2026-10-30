"""Run after all experiments and notebook execution; validate real artifacts."""
import csv
import json
from pathlib import Path

import numpy as np
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

from src.common import ROOT, read_json, sha256, source_hashes, write_json, now
from src.phases.phase_04_train import fingerprint, provenance, score
from src.phases.phase_05_evaluate import metrics


def verify():
    summary = read_json(ROOT / 'outputs/report/summary.json')
    selection = read_json(ROOT / 'outputs/experiments/selection.json')
    assert summary['status'] == 'COMPLETED'
    assert selection['provenance_hash'] == fingerprint(provenance())
    runs = []
    for number in range(1, 8):
        directory = ROOT / f'outputs/experiments/R{number:02d}'
        result = read_json(directory / 'result.json')
        expected = 5 if number < 7 else 3
        assert result['status'] == 'COMPLETED'
        assert len(result['history']) == expected
        assert result['best'] == min(result['history'], key=score)
        assert [r['epoch'] for r in result['history']] == list(range(1, expected + 1))
        assert all(r['train_samples'] == summary['data_counts']['train'] and r['val_samples'] == summary['data_counts']['validation'] for r in result['history'])
        for name, checksum in result['checkpoint_hashes'].items():
            assert sha256(directory / name) == checksum
        events = EventAccumulator(str(directory / 'tensorboard')).Reload()
        for prefix, field in [('train', 'train'), ('validation', 'val')]:
            for metric in ('loss', 'accuracy', 'seconds'):
                scalars = events.Scalars(f'{prefix}/{metric}')
                assert [s.step for s in scalars] == list(range(1, expected + 1))
                np.testing.assert_allclose([s.value for s in scalars], [r[f'{field}_{metric}'] for r in result['history']], rtol=1e-6)
        runs.append(result)
    assert selection['final_run'] == min(runs, key=lambda r: score(r['best']))['id']
    for evaluation in summary['test']:
        path = ROOT / f'outputs/report/{evaluation["run"]}_predictions.csv'
        assert sha256(path) == evaluation['predictions_sha256']
        with path.open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        cm = np.zeros((6, 6), dtype=int)
        for row in rows:
            cm[int(row['truth']), int(row['prediction'])] += 1
        assert len(rows) == summary['data_counts']['test'] == 3000
        assert cm.tolist() == evaluation['confusion_matrix']
        recomputed = metrics(cm)
        assert recomputed['accuracy'] == evaluation['accuracy']
        assert recomputed['macro_f1'] == evaluation['macro_f1']
        assert selection['selected_before_test'] <= evaluation['evaluated']
    notebook = read_json(ROOT / 'outputs/notebooks/main.executed.ipynb')
    code = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']
    assert all(cell['execution_count'] is not None for cell in code)
    assert not any(output.get('output_type') == 'error' for cell in code for output in cell['outputs'])
    assert any(output.get('data', {}).get('image/png') for cell in code for output in cell['outputs'])
    result = {'status': 'PASSED', 'time': now(), 'runs': len(runs), 'epochs': sum(len(r['history']) for r in runs),
              'test_evaluations': len(summary['test']), 'test_samples_each': 3000,
              'tensorboard_tags_per_run': 6, 'notebook_executed_cells': len(code), 'source_hashes': source_hashes()}
    write_json(ROOT / 'outputs/verification.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    verify()
