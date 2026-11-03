"""Build a fresh scene-grouped manifest from the reviewed EDA candidates."""
import csv
import hashlib
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.common import sha256, write_json
from src.phases.phase_02_data import CLASSES, RAW, inspect_images, locate, make_split


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build(target):
    if target.exists():
        raise FileExistsError(target)
    dev = inspect_images(locate('seg_train'), 'train')
    test = inspect_images(locate('seg_test'), 'test')
    rows, rejected = make_split(dev, test, 42, True)
    by_path = {r['relative_path']: r for r in rows}
    parent = {p:p for p in by_path}

    def find(p):
        while parent[p] != p:
            p = parent[p]
        return p

    review = Path(__file__).with_name('review.csv')
    with review.open(encoding='utf-8-sig') as f:
        pairs = list(csv.DictReader(f))
    original = ROOT/'outputs/eda-seed42/near-pairs.csv'
    with original.open(encoding='utf-8-sig') as f:
        candidates = list(csv.DictReader(f))
    assert len(pairs) == len(candidates) == 356
    uncertain = set()
    for p, old in zip(pairs, candidates):
        assert all(p[k] == v for k,v in old.items())
        a,b = p['a'],p['b']
        assert a in parent and b in parent
        if p['decision']=='same_scene':
            x,y = sorted((find(a),find(b)))
            parent[y] = x
        elif p['decision']=='uncertain':
            uncertain.update((a,b))
        else:
            assert p['decision']=='different_scene'
    groups = defaultdict(list)
    for path,r in sorted(by_path.items()):
        groups[find(path)].append(r)
    eligible = defaultdict(list)
    kept = []
    for anchor,members in sorted(groups.items()):
        gid = hashlib.sha256(anchor.encode()).hexdigest()
        has_test = any(r['split']=='test' for r in members)
        ambiguous = any(r['relative_path'] in uncertain for r in members)
        conflict = len({r['label'] for r in members})>1
        for r in members:
            r['group_id'] = gid
            if r['split']=='test':
                kept.append(r)
            elif has_test or ambiguous or conflict:
                reason = 'scene_touches_test' if has_test else 'scene_label_conflict' if conflict else 'unresolved_pair'
                rejected.append({**r,'reason':reason})
        if not (has_test or ambiguous or conflict):
            eligible[members[0]['class_name']].append(members)
    rng=random.Random(42)
    for c in CLASSES:
        blocks=eligible[c]
        rng.shuffle(blocks)
        need=round(sum(map(len,blocks))*.2)
        for block in blocks:
            val=len(block)<=need
            if val: need-=len(block)
            for r in block:
                r['split']='validation' if val else 'train'
                kept.append(r)
        assert need==0
    kept.sort(key=lambda r:(r['split'],r['relative_path']))
    paths={r['relative_path']:r['split'] for r in kept}
    assert {p for p,s in paths.items() if s=='test'}=={r['relative_path'] for r in test}
    assert len(paths)==len(kept) and len(kept)+len(rejected)==len(dev)+len(test)
    assert set(paths).isdisjoint(r['relative_path'] for r in rejected)
    for key in ['group_id','sha256']:
        splits=defaultdict(set)
        for r in kept: splits[r[key]].add(r['split'])
        assert all(len(ss)==1 for ss in splits.values())
    for p in pairs:
        if p['decision']!='different_scene' and p['a'] in paths and p['b'] in paths:
            assert paths[p['a']]==paths[p['b']]
    counts={s:dict(Counter(r['class_name'] for r in kept if r['split']==s)) for s in ['train','validation','test']}
    assert all(set(counts[s])==set(CLASSES) for s in counts)
    with TemporaryDirectory(dir=target.parent) as tmp:
        stage=Path(tmp)/'data'
        stage.mkdir()
        write_csv(stage/'manifest.csv',kept)
        write_csv(stage/'excluded.csv',[{k:r.get(k,'') for k in ('relative_path','class_name','sha256','group_id','reason')} for r in rejected])
        audit=dict(status='PASSED',split_version='scene-review-v1',image_hash='sha256-rgb-size-v1',seed=42,classes=CLASSES,
                   counts=counts,original_train=len(dev),original_test=len(test),removed_train_duplicates=rejected,
                   prediction_images=sum(p.is_file() for p in (RAW/'seg_pred').rglob('*')),
                   review_sha256=sha256(review),candidates_sha256=sha256(original),manifest_sha256=sha256(stage/'manifest.csv'))
        write_json(stage/'audit.json',audit)
        stage.rename(target)
    print(counts,Counter(r['reason'] for r in rejected),flush=True)


if __name__=='__main__':
    build(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'outputs/data')
