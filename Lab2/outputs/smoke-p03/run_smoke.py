"""Run the P03 checkpoint smoke on a balanced subset of the scene manifest."""
import csv
import gc
import math
import random
import sys
from pathlib import Path
from datetime import datetime

import torch
from torch.utils.data import DataLoader, Subset
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from torch.utils.tensorboard import SummaryWriter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.common import now, read_json, sha256, write_json
from src.phases.phase_02_data import Scenes, MANIFEST, RAW, rgb_digest, CLASSES
from src.phases.phase_03_models import build
from src.phases.phase_04_train import epoch, save_checkpoint, score, seed_all, rng_state
from PIL import Image


def subset(split, output):
    data = Scenes(split)
    rng = random.Random(42)
    indices = []
    for label in range(len(CLASSES)):
        indices.extend(rng.sample([i for i,r in enumerate(data.rows) if int(r['label']) == label], 4))
    paths = []
    for i in indices:
        r = data.rows[i]
        with Image.open(RAW/r['relative_path']) as image:
            assert rgb_digest(image) == r['sha256']
        paths.append(r['relative_path'])
    write_json(output/f'{split}.json', paths)
    return Subset(data, indices)


def run_model(name, device, train, val, root, manifest_hash):
    folder = root/name
    folder.mkdir()
    seed_all(42)
    generator = torch.Generator().manual_seed(42)
    batches = DataLoader(train, batch_size=8, shuffle=True, generator=generator)
    validation = DataLoader(val, batch_size=8)
    best = None
    history = []
    handoff = None
    stale = 0
    reference_loss = None
    with SummaryWriter(str(folder/'tensorboard')) as writer:
        for stage, numbers, lr in [('transfer',range(1,6),3e-4), ('finetune',range(6,8),1e-5)]:
            model = build(name,stage,42).to(device)
            if stage == 'finetune':
                handoff = torch.load(folder/'handoff.pt',map_location='cpu',weights_only=True)
                model.load_state_dict(handoff['model'],strict=True)
                check = epoch(model,validation,device)
                assert check['accuracy']==best['val_accuracy'] and math.isclose(check['loss'],best['val_loss'],abs_tol=1e-5)
                reference_loss = check['loss']
                print(name,'handoff from',handoff['epoch'],flush=True)
                handoff = handoff['epoch']
            optimizer = torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=lr)
            for number in numbers:
                t = epoch(model,batches,device,optimizer)
                v = epoch(model,validation,device)
                row = dict(epoch=number,stage=stage,lr=lr,train_loss=t['loss'],val_loss=v['loss'],
                           train_accuracy=t['accuracy'],val_accuracy=v['accuracy'],train_samples=t['samples'],
                           val_samples=v['samples'],epoch_time=t['seconds']+v['seconds'],handoff_epoch=handoff)
                improved = best is None or score(row)<score(best)
                if improved:
                    best = row.copy()
                row.update(best_epoch=best['epoch'],best_val_accuracy=best['val_accuracy'],checkpoint_saved=improved)
                history.append(row)
                if stage=='finetune':
                    if reference_loss-v['loss']>=1e-4: reference_loss,stale=v['loss'],0
                    else: stale+=1
                state = dict(model=model.state_dict(),model_name=name,epoch=number,stage=stage,metrics=row,
                             manifest_sha256=manifest_hash,classes=CLASSES,eval_transform=str(val.dataset.transform))
                if improved:
                    save_checkpoint(folder/'best.pt',state)
                    if stage=='transfer': save_checkpoint(folder/'handoff.pt',state)
                save_checkpoint(folder/'last.pt',{**state,'optimizer':optimizer.state_dict(),'history':history,
                                'rng':rng_state(generator,device),'stale':stale,'reference_loss':reference_loss})
                for key in ('train_loss','val_loss','train_accuracy','val_accuracy','best_val_accuracy','lr'):
                    writer.add_scalar(key,row[key],number)
                writer.flush()
                write_json(folder/'history.json',history)
                print(name,stage,number,'val',v['accuracy'],v['loss'],'best',best['epoch'],flush=True)
                del state
            del model, optimizer
            gc.collect()
    best_disk = torch.load(folder/'best.pt',map_location='cpu',weights_only=True)
    winner = min(read_json(folder/'history.json'),key=score)
    assert best_disk['epoch']==winner['epoch']==history[-1]['best_epoch']
    model=build(name,best_disk['stage'],42).to(device)
    model.load_state_dict(best_disk['model'])
    del best_disk
    actual=epoch(model,validation,device)
    assert actual['accuracy']==winner['val_accuracy'] and math.isclose(actual['loss'],winner['val_loss'],abs_tol=1e-5)
    last=torch.load(folder/'last.pt',map_location='cpu',weights_only=False)
    assert last['epoch']==7 and last['metrics']==history[-1] and last['optimizer']['state'] and last['rng']
    series=EventAccumulator(str(folder/'tensorboard')).Reload().Scalars('val_accuracy')
    assert [e.step for e in series]==list(range(1,8)) and all(abs(e.value-r['val_accuracy'])<1e-6 for e,r in zip(series,history))
    result=dict(status='PASSED',model=name,handoff_epoch=handoff,best_epoch=winner['epoch'],validation_reload=actual,
                last_epoch=7,stop_reason='smoke_epoch_budget',best_sha256=sha256(folder/'best.pt'))
    write_json(folder/'result.json',result)
    return result


if __name__=='__main__':
    root=Path(__file__).parent/datetime.now().strftime('%Y%m%d-%H%M%S')
    root.mkdir()
    preflight=read_json(ROOT/'outputs/models/preflight.json')
    manifest_hash=sha256(MANIFEST)
    assert preflight['status']=='PASSED' and preflight['manifest_sha256']==manifest_hash
    train,val=(subset(s,root) for s in ('train','validation'))
    results=[run_model(n,preflight['device'],train,val,root,manifest_hash) for n in ('vgg11','densenet121')]
    write_json(root/'report.json',dict(status='PASSED',finished=now(),device=preflight['device'],
               manifest_sha256=manifest_hash,seed=42,train_samples=len(train),val_samples=len(val),models=results))
    print(root,'PASSED',flush=True)
