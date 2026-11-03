"""Scene-grouped two-stage training, validation selection and epoch-boundary resume."""
import gc
import hashlib
import importlib.metadata
import json
from pathlib import Path
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


def stop_state(loss, reference, stale, delta=1e-4):
    if reference - loss >= delta:
        return loss, 0
    return reference, stale + 1


def datasets(smoke):
    from PIL import Image
    from torch.utils.data import Subset
    from src.phases.phase_02_data import Scenes, RAW, rgb_digest, CLASSES
    result = []
    for split in ('train', 'validation'):
        data = Scenes(split)
        indices = list(range(len(data)))
        if smoke:
            rng = random.Random(42)
            indices = [i for label in range(len(CLASSES)) for i in
                       rng.sample([j for j,r in enumerate(data.rows) if int(r['label']) == label], 4)]
        for i in indices:
            row = data.rows[i]
            with Image.open(RAW / row['relative_path']) as image:
                if rgb_digest(image) != row['sha256']:
                    raise ValueError(f"Pixel content changed: {row['relative_path']}")
        result.append(Subset(data, indices))
    return result


def train_stages(folder, name, device, data, spec, parent=None, pause_after=None):
    import shutil
    from torch.utils.data import DataLoader
    from src.phases.phase_02_data import CLASSES
    folder.mkdir(exist_ok=True, parents=True)
    identity = {'model':name, 'spec':spec, 'device':device, 'manifest':sha256(MANIFEST),
                'sources':source_hashes(), 'weights':read_json(ROOT/'outputs/models/weights.json')[name]['sha256'],
                'parent':sha256(parent/'handoff.pt') if parent else None,
                'branch_rng':sha256(parent/'branch-rng.pt') if parent else None}
    key = fingerprint(identity)
    meta = folder/'identity.json'
    if meta.exists() and read_json(meta)!=identity:
        raise ValueError(f'Stale run in {folder}')
    if not meta.exists() and any(folder.iterdir()):
        raise ValueError(f'Unidentified output: {folder}')
    write_json(meta,identity)
    def log(msg):
        line=f'{now()} {folder.name} {msg}'
        with (folder/'run.log').open('a',encoding='utf8') as f: print(line,file=f)
        print(line,flush=True)

    seed_all(42)
    gen=torch.Generator().manual_seed(42)
    tr=DataLoader(data[0],batch_size=8,shuffle=True,generator=gen)
    va=DataLoader(data[1],batch_size=8)
    last=folder/'last.pt'
    history=[]
    best=None
    stale=0
    ref=None
    model=optimizer=None
    stage=None
    handoff_epoch=None
    def setup(mode,lr):
        m=build(name,mode,42).to(device)
        return m,torch.optim.Adam([p for p in m.parameters() if p.requires_grad],lr=lr)
    def load(path):
        return torch.load(path,map_location='cpu',weights_only=False)
    if last.exists():
        ck=load(last)
        if ck['fingerprint']!=key: raise ValueError('Resume identity mismatch')
        history,best,stage,stale,ref,handoff_epoch=(ck[k] for k in ('history','best','stage','stale','reference','handoff_epoch'))
        model,optimizer=setup(stage,history[-1]['learning_rate'])
        model.load_state_dict(ck['model']); optimizer.load_state_dict(ck['optimizer'])
        restore_rng(ck['rng'],gen)
        if best['epoch']==ck['epoch']:
            save_checkpoint(folder/'best.pt',ck)
            if stage=='transfer': save_checkpoint(folder/'handoff.pt',ck)
        if ck['epoch']==5: save_checkpoint(folder/'branch-rng.pt',ck['rng'])
        del ck
        log(f"resume after epoch {history[-1]['epoch']}")
    elif parent:
        shutil.copyfile(parent/'handoff.pt',folder/'best.pt')
        base=load(folder/'best.pt')
        best=base['best']
        del base
    start=history[-1]['epoch']+1 if history else (6 if parent else 1)
    log(f'start epoch {start}')
    with SummaryWriter(str(folder/'tensorboard'),purge_step=history[0]['epoch'] if history else None) as writer:
        def scalars(row):
            for field in ('train_loss','val_loss','train_accuracy','val_accuracy','learning_rate','best_val_accuracy'):
                writer.add_scalar(field,row[field],row['epoch'])
        for old in history: scalars(old)
        try:
            for number in range(start,spec['max_epoch']+1):
                if stale>=3: break
                mode='transfer' if number<=5 else 'finetune'
                lr=3e-4 if number<=5 else spec['fine_lr']
                if stage!=mode:
                    model,optimizer=setup(mode,lr)
                    stage=mode
                    if number==6:
                        source=parent or folder
                        ck=load(source/'handoff.pt')
                        model.load_state_dict(ck['model'])
                        handoff_epoch=ck['epoch']
                        ref=ck['best']['val_loss']
                        v=epoch(model,va,device)
                        if v['accuracy']!=ck['best']['val_accuracy'] or abs(v['loss']-ref)>1e-5:
                            raise ValueError('Handoff validation mismatch')
                        del ck
                        restore_rng(load(source/'branch-rng.pt'),gen)
                        log(f'handoff epoch {handoff_epoch}, new Adam LR {lr}')
                t=epoch(model,tr,device,optimizer); v=epoch(model,va,device)
                row=dict(id=folder.name,model=name,stage=stage,epoch=number,learning_rate=lr,
                         train_samples=t['samples'],val_samples=v['samples'],train_loss=t['loss'],
                         train_accuracy=t['accuracy'],val_accuracy=v['accuracy'],val_loss=v['loss'],
                         epoch_time=t['seconds']+v['seconds'],handoff_epoch=handoff_epoch)
                improved=best is None or score(row)<score(best)
                if improved: best=row.copy()
                if stage=='finetune': ref,stale=stop_state(v['loss'],ref,stale)
                row.update(best_epoch=best['epoch'],best_val_accuracy=best['val_accuracy'],checkpoint_saved=improved,stale=stale)
                history.append(row)
                ck=dict(fingerprint=key,model=model.state_dict(),model_name=name,stage=stage,classes=CLASSES,
                        eval_transform=str(data[1].dataset.transform),epoch=number,optimizer=optimizer.state_dict(),
                        rng=rng_state(gen,device),reference=ref,stale=stale,best=best,history=history,handoff_epoch=handoff_epoch)
                save_checkpoint(last,ck)
                if improved:
                    save_checkpoint(folder/'best.pt',ck)
                    if stage=='transfer': save_checkpoint(folder/'handoff.pt',ck)
                if number==5: save_checkpoint(folder/'branch-rng.pt',ck['rng'])
                del ck
                write_json(folder/'history.json',history)
                scalars(row); writer.flush()
                log(f"epoch {number} val_accuracy={v['accuracy']} val_loss={v['loss']} best={best['epoch']} saved={improved} stale={stale}")
                if pause_after==number and stale<3 and number<spec['max_epoch']:
                    return {'status':'PAUSED','epoch':number}
        finally: writer.close()
    write_json(folder/'history.json',history)
    ck=load(folder/'best.pt')
    model.load_state_dict(ck['model'])
    actual=epoch(model,va,device)
    if ck['epoch']!=best['epoch'] or actual['accuracy']!=best['val_accuracy'] or abs(actual['loss']-best['val_loss'])>1e-5:
        raise ValueError('Best reload mismatch')
    result=dict(status='COMPLETED',id=folder.name,device=device,best=best,history=history,validation_reload=actual,
                stop_reason='early_stopping' if stale>=3 else 'epoch_budget',fingerprint=key)
    write_json(folder/'result.json',result)
    log(result['stop_reason'])
    return result


def run(smoke=False,pause_after=None):
    from src.phases.phase_02_data import OUT as DATA
    audit=read_json(DATA/'audit.json')
    preflight=read_json(ROOT/'outputs/models/preflight.json')
    if audit['split_version']!='scene-review-v1' or sha256(MANIFEST)!=audit['manifest_sha256'] or preflight['manifest_sha256']!=audit['manifest_sha256'] or preflight['status']!='PASSED':
        raise ValueError('Manifest or P02 preflight mismatch')
    # Only a change to the training module is independent of the P02 model checks.
    current=source_hashes()
    exclude=str(Path(__file__).resolve().relative_to(ROOT))
    if {k:v for k,v in current.items() if k!=exclude}!={k:v for k,v in preflight['source_hashes'].items() if k!=exclude}:
        raise ValueError('P02 sources changed')
    if pause_after and not smoke: raise ValueError('pause_after is smoke-only')
    data=datasets(smoke)
    root=ROOT/'outputs'/('smoke-entry-p03' if smoke else 'training-scene-v1')
    spec={'seed':42,'batch':8,'max_epoch':9 if smoke else 20,'fine_lr':1e-5,'smoke':smoke}
    results=[]
    for name in ('vgg11','densenet121','vgg11-lr-ablation'):
        branch=name.endswith('ablation')
        result=train_stages(root/name,'vgg11' if branch else name,preflight['device'],data,
                            {**spec,'fine_lr':3e-6 if branch else 1e-5},root/'vgg11' if branch else None,pause_after)
        if result['status']=='PAUSED': return result
        results.append(result)
        gc.collect()
    selected=min(results[:2],key=lambda r:score(r['best']))
    report=dict(status='PASSED',smoke=smoke,selected_by_validation=selected['id'],runs=[r['id'] for r in results],manifest=sha256(MANIFEST))
    write_json(root/'report.json',report)
    return report


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--smoke',action='store_true')
    parser.add_argument('--pause-after',type=int)
    args=parser.parse_args()
    print(run(args.smoke,args.pause_after))
