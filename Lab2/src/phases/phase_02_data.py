"""Download, audit, split and load Intel scene images without changing raw files."""
import csv
import math
import random
import stat
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import requests
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from torchvision.models import DenseNet121_Weights

from src.common import ROOT, config, now, read_json, sha256, write_json

CLASSES = ['buildings', 'forest', 'glacier', 'mountain', 'sea', 'street']
RAW = ROOT / 'data/raw/intel-v2'
OUT = ROOT / 'outputs/data'
MANIFEST = OUT / 'manifest.csv'


def download(url, destination):
    destination = Path(destination)
    if destination.exists():
        return destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + '.part')
    with requests.get(url, stream=True, timeout=(30, 120)) as response:
        response.raise_for_status()
        expected = int(response.headers.get('content-length', 0))
        count, notified = 0, 0
        with partial.open('wb') as f:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
                    count += len(chunk)
                    if count - notified >= 32 * 1024 * 1024:
                        print(f'Download {destination.name}: {count / 1e6:.1f} MB', flush=True)
                        notified = count
        if expected and expected != count:
            raise IOError(f'Incomplete download: {count} != {expected}')
    partial.replace(destination)
    return destination


def safe_extract(archive, destination):
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError(destination)
    with zipfile.ZipFile(archive) as z:
        for item in z.infolist():
            target = (destination / item.filename).resolve()
            if not target.is_relative_to(destination) or stat.S_ISLNK(item.external_attr >> 16):
                raise ValueError(f'Unsafe archive entry: {item.filename}')
        destination.mkdir(parents=True)
        z.extractall(destination)


def locate(name):
    candidates = [p for p in RAW.rglob(name) if p.is_dir() and
                  sorted(q.name for q in p.iterdir() if q.is_dir()) == CLASSES]
    if len(candidates) != 1:
        raise ValueError(f'Ambiguous or invalid {name}: {candidates}')
    return candidates[0]


def inspect_images(folder, split):
    rows = []
    for label, name in enumerate(CLASSES):
        for path in sorted((folder / name).iterdir()):
            if not path.is_file():
                raise ValueError(f'Unexpected subdirectory: {path}')
            with Image.open(path) as image:
                image.load()
                width, height = image.size
                if width < 1 or height < 1:
                    raise ValueError(f'Invalid image size: {path}')
                rows.append(dict(relative_path=path.relative_to(RAW).as_posix(), split=split,
                                 class_name=name, label=label, sha256=sha256(path),
                                 width=width, height=height, original_mode=image.mode))
    return rows


def make_split(train, test, seed=42, quarantine_conflicts=False):
    labels = defaultdict(set)
    for row in train + test:
        labels[row['sha256']].add(row['label'])
    conflicts = {h: sorted(v) for h, v in labels.items() if len(v) > 1}
    if conflicts and not quarantine_conflicts:
        raise ValueError(f'Conflicting labels for identical images: {conflicts}')
    seen = {r['sha256'] for r in test}
    retained, removed = [], []
    for row in sorted(train, key=lambda r: r['relative_path']):
        if row['sha256'] in seen or row['sha256'] in conflicts:
            removed.append({**row, 'reason': 'conflicting_labels' if row['sha256'] in conflicts else 'duplicate_or_test_overlap'})
        else:
            seen.add(row['sha256'])
            retained.append(dict(row))
    generator = random.Random(seed)
    result = []
    for label in range(6):
        group = [r for r in retained if r['label'] == label]
        if len(group) < 2:
            raise ValueError(f'Not enough images for class {label}')
        generator.shuffle(group)
        count = max(1, min(len(group) - 1, math.floor(0.2 * len(group))))
        for i, row in enumerate(group):
            row['split'] = 'validation' if i < count else 'train'
            result.append(row)
    result.extend(test)
    for a, b in [('train', 'validation'), ('train', 'test'), ('validation', 'test')]:
        if {r['sha256'] for r in result if r['split'] == a} & {r['sha256'] for r in result if r['split'] == b}:
            raise ValueError('Split leakage')
    return sorted(result, key=lambda r: (r['split'], r['relative_path'])), removed


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    if (OUT / 'audit.json').exists():
        audit = read_json(OUT / 'audit.json')
        if audit['manifest_sha256'] != sha256(MANIFEST):
            raise ValueError('Manifest changed since audit')
        return audit
    archive = ROOT / 'data/downloads/intel-v2.zip'
    url = 'https://www.kaggle.com/api/v1/datasets/download/puneet6060/intel-image-classification?datasetVersionNumber=2'
    download(url, archive)
    if not zipfile.is_zipfile(archive):
        raise ValueError('Kaggle response is not a ZIP archive')
    marker = ROOT / 'data/raw/intel-v2.extracted.json'
    if not RAW.exists():
        safe_extract(archive, RAW)
        write_json(marker, {'archive_sha256': sha256(archive)})
    if not marker.exists() or read_json(marker)['archive_sha256'] != sha256(archive):
        raise ValueError('Raw extraction incomplete or archive changed')
    train = inspect_images(locate('seg_train'), 'train')
    test = inspect_images(locate('seg_test'), 'test')
    rows, removed = make_split(train, test, config()['seed'], quarantine_conflicts=True)
    with MANIFEST.open('x', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    counts = {split: dict(Counter(r['class_name'] for r in rows if r['split'] == split))
              for split in ['train', 'validation', 'test']}
    audit = {'status': 'PASSED', 'time': now(), 'version': 2, 'url': url,
             'archive_bytes': archive.stat().st_size, 'archive_sha256': sha256(archive),
             'manifest_sha256': sha256(MANIFEST), 'classes': CLASSES,
             'original_train': len(train), 'original_test': len(test), 'counts': counts,
             'removed_train_duplicates': removed,
             'test_internal_duplicates': len(test) - len({r['sha256'] for r in test}),
             'prediction_images': sum(1 for p in RAW.rglob('*') if p.is_file() and 'seg_pred' in p.parts)}
    write_json(OUT / 'audit.json', audit)
    print(json_summary(audit), flush=True)
    return audit


def json_summary(audit):
    return str({'counts': audit['counts'], 'removed': len(audit['removed_train_duplicates'])})


class Scenes(Dataset):
    def __init__(self, split):
        with MANIFEST.open(newline='', encoding='utf-8') as f:
            self.rows = [r for r in csv.DictReader(f) if r['split'] == split]
        if not self.rows:
            raise ValueError(f'Empty split: {split}')
        self.transform = (transforms.Compose([
            transforms.Resize(256), transforms.RandomCrop(224), transforms.RandomHorizontalFlip(),
            transforms.ToTensor(), transforms.Normalize([.485, .456, .406], [.229, .224, .225])
        ]) if split == 'train' else DenseNet121_Weights.IMAGENET1K_V1.transforms())

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        row = self.rows[index]
        with Image.open(RAW / row['relative_path']) as image:
            return self.transform(image.convert('RGB')), int(row['label'])


def loader(split, batch, generator=None):
    return DataLoader(Scenes(split), batch_size=batch, shuffle=split == 'train',
                      num_workers=0, drop_last=False, generator=generator)


if __name__ == '__main__':
    run()
