import copy
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, TensorDataset

from src.phases import phase_02_data as data
from src.phases import phase_04_train as train
from src.phases.phase_05_evaluate import metrics


def fixture():
    return [dict(relative_path=f'{label}/{i}.jpg', label=label, sha256=f'{label}-{i}', split='train')
            for label in range(6) for i in range(10)]


class DataTests(unittest.TestCase):
    def test_split_deduplicates_and_has_no_leakage(self):
        rows = fixture()
        rows.append({**rows[0], 'relative_path': 'duplicate.jpg'})
        test = [{**rows[1], 'relative_path': 'test.jpg', 'split': 'test'}]
        result, removed = data.make_split(rows, test)
        self.assertEqual(len(removed), 2)
        self.assertEqual((result, removed), data.make_split(rows, test))
        sets = {s: {r['sha256'] for r in result if r['split'] == s} for s in ('train', 'validation', 'test')}
        self.assertFalse(sets['train'] & sets['validation'] | sets['train'] & sets['test'] | sets['validation'] & sets['test'])

    def test_conflict_fails_unless_explicit_quarantine(self):
        rows = fixture()
        rows.append({**rows[0], 'label': 1, 'relative_path': 'conflict.jpg'})
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            data.make_split(rows, [])
        result, removed = data.make_split(rows, [], quarantine_conflicts=True)
        self.assertEqual(len(removed), 2)
        self.assertFalse(any(r['sha256'] == rows[0]['sha256'] for r in result))

    def test_archive_traversal_rejected_before_extract(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            archive = folder / 'bad.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('../escape.txt', 'unsafe')
            with self.assertRaises(ValueError):
                data.safe_extract(archive, folder / 'raw')
            self.assertFalse((folder / 'raw').exists())
            self.assertFalse((folder / 'escape.txt').exists())

    def test_corrupt_image_fails(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            for label in data.CLASSES:
                (folder / label).mkdir()
                Image.new('RGB', (8, 8)).save(folder / label / 'valid.jpg')
            (folder / data.CLASSES[-1] / 'corrupt.jpg').write_bytes(b'broken')
            with patch.object(data, 'RAW', folder), self.assertRaises(OSError):
                data.inspect_images(folder, 'train')


class TrainTests(unittest.TestCase):
    def test_weighted_metrics_and_no_validation_graph(self):
        model = torch.nn.Linear(2, 6)
        x = torch.tensor([[1., 0.], [0., 1.], [2., 3.], [-1., 0.], [4., 2.]])
        y = torch.tensor([0, 1, 2, 3, 4])
        with torch.no_grad():
            expected = torch.nn.functional.cross_entropy(model(x), y).item()
            accuracy = (model(x).argmax(1) == y).float().mean().item()
        seen = []
        hook = model.register_forward_hook(lambda m, args, output: seen.append(output.requires_grad))
        actual = train.epoch(model, DataLoader(TensorDataset(x, y), batch_size=2), 'cpu')
        hook.remove()
        self.assertAlmostEqual(actual['loss'], expected, places=6)
        self.assertAlmostEqual(actual['accuracy'], accuracy, places=6)
        self.assertEqual(actual['samples'], 5)
        self.assertEqual(seen, [False, False, False])

    def test_epoch_resume_matches_uninterrupted_and_rejects_stale(self):
        def model(*args):
            torch.manual_seed(42)
            net = torch.nn.Sequential(torch.nn.Linear(2, 3), torch.nn.Linear(3, 6))
            net[0].requires_grad_(False)
            return net

        dataset = TensorDataset(torch.arange(14).float().reshape(7, 2) / 14, torch.arange(7) % 6)
        def batches(split, batch, generator=None):
            return DataLoader(dataset, batch_size=batch, shuffle=split == 'train', generator=generator)

        spec = dict(id='R01', model='fixture', mode='transfer', batch=3, lr=.001, epochs=2)
        with tempfile.TemporaryDirectory() as folder, patch.object(train, 'build', side_effect=model), patch.object(train, 'loader', side_effect=batches):
            folder = Path(folder)
            with patch.object(train, 'OUT', folder / 'full'):
                full = train.train_run(spec, 'cpu', {})
                expected = torch.load(folder / 'full/R01/last.pt', weights_only=False)
            original_epoch = train.epoch
            calls = 0
            def interrupted(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 3:
                    raise RuntimeError('simulated interruption')
                return original_epoch(*args, **kwargs)
            with patch.object(train, 'OUT', folder / 'resume'):
                with patch.object(train, 'epoch', side_effect=interrupted), self.assertRaisesRegex(RuntimeError, 'simulated'):
                    train.train_run(spec, 'cpu', {})
                resumed = train.train_run(spec, 'cpu', {})
                actual = torch.load(folder / 'resume/R01/last.pt', weights_only=False)
                with self.assertRaisesRegex(ValueError, 'Stale'):
                    train.train_run({**spec, 'lr': .01}, 'cpu', {})
            self.assertEqual(full['best']['epoch'], resumed['best']['epoch'])
            self.assertEqual(actual['epoch'], 2)
            for key in expected['model']:
                self.assertTrue(torch.equal(expected['model'][key], actual['model'][key]), key)
            initial = model().state_dict()
            self.assertTrue(torch.equal(initial['0.weight'], actual['model']['0.weight']))
            self.assertFalse(torch.equal(initial['1.weight'], actual['model']['1.weight']))


class EvaluationTests(unittest.TestCase):
    def test_confusion_metrics_zero_division_and_counts(self):
        cm = np.zeros((6, 6), dtype=int)
        cm[0, 0], cm[0, 1], cm[1, 1], cm[2, 1] = 2, 1, 3, 1
        result = metrics(cm)
        self.assertEqual(result['samples'], 7)
        self.assertAlmostEqual(result['accuracy'], 5 / 7)
        self.assertAlmostEqual(result['per_class'][0]['precision'], 1)
        self.assertAlmostEqual(result['per_class'][0]['recall'], 2 / 3)
        self.assertEqual(result['per_class'][2]['precision'], 0)
        self.assertAlmostEqual(result['macro_f1'], (.8 + .75) / 6)


if __name__ == '__main__':
    unittest.main()
