"""P04: evaluate the validation-selected normal checkpoint on the scene manifest."""
import csv
import math
from collections import Counter

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image

from src.common import ROOT, now, read_json, write_json, sha256
from src.phases.phase_02_data import CLASSES, RAW, MANIFEST, loader, rgb_digest
from src.phases.phase_03_models import build
from src.phases.phase_04_train import epoch, fingerprint
from src.phases.phase_05_evaluate import metrics, write_csv

OUT = ROOT/'outputs/evaluation-scene-v1'


def run():
    runs = ROOT/'outputs/training-scene-v1'
    selection = read_json(runs/'report.json')
    audit = read_json(MANIFEST.parent/'audit.json')
    assert selection['status']=='PASSED' and not selection['smoke']
    assert sha256(MANIFEST)==selection['manifest']==audit['manifest_sha256']
    name = selection['selected_by_validation']
    folder = runs/name
    result = read_json(folder/'result.json')
    best = result['best']
    identity = read_json(folder/'identity.json')
    path = folder/'best.pt'
    version = dict(model=name,epoch=best['epoch'],manifest=selection['manifest'],checkpoint_sha256=sha256(path))
    OUT.mkdir(exist_ok=True)
    cache = OUT/'metrics.json'
    if cache.exists():
        saved = read_json(cache)
        if saved['version']!=version or saved['predictions_sha256']!=sha256(OUT/'predictions.csv'):
            raise ValueError('Saved evaluation does not match inputs')
        return saved
    ck = torch.load(path,map_location='cpu',weights_only=False)
    assert ck['model_name']==name and ck['epoch']==best['epoch'] and ck['classes']==CLASSES
    assert ck['fingerprint']==result['fingerprint']==fingerprint(identity)
    device = identity['device']
    model = build(name,ck['stage']).to(device).eval()
    model.load_state_dict(ck['model'],strict=True)
    validation = loader('validation',8)
    assert ck['eval_transform']==str(validation.dataset.transform)
    check = epoch(model,validation,device)
    assert check['accuracy']==best['val_accuracy'] and math.isclose(check['loss'],best['val_loss'],abs_tol=1e-5)
    print('PASS validation reload:',check,flush=True)
    del ck
    test = loader('test',8)
    rows = test.dataset.rows
    assert len(rows)==len({r['relative_path'] for r in rows})==3000
    assert str(test.dataset.transform)==str(validation.dataset.transform)
    for row in rows:
        with Image.open(RAW/row['relative_path']) as im:
            if rgb_digest(im)!=row['sha256']: raise ValueError(row['relative_path'])
    preds=[]
    loss_sum=0.
    with torch.inference_mode():
        for images,labels in test:
            logits=model(images.to(device))
            loss=torch.nn.functional.cross_entropy(logits,labels.to(device),reduction='sum')
            assert torch.isfinite(loss)
            loss_sum+=loss.item()
            scores,indices=logits.softmax(1).max(1)
            for truth,guess,score in zip(labels.tolist(),indices.tolist(),scores.tolist()):
                row=rows[len(preds)]
                assert int(row['label'])==truth
                preds.append(dict(path=row['relative_path'],truth=CLASSES[truth],predicted=CLASSES[guess],softmax=score))
    write_csv(OUT/'predictions.csv',preds)
    with (OUT/'predictions.csv').open(encoding='utf-8-sig') as f:
        disk=list(csv.DictReader(f))
    assert [r['path'] for r in disk]==[r['relative_path'] for r in rows]
    cm=np.zeros((6,6),dtype=int)
    for r in disk: cm[CLASSES.index(r['truth']),CLASSES.index(r['predicted'])]+=1
    scores=metrics(cm)
    errors=[r for r in disk if r['truth']!=r['predicted']]
    assert cm.sum()==3000 and cm.trace()==3000-len(errors)
    assert cm.sum(axis=1).tolist()==[audit['counts']['test'][c] for c in CLASSES]
    assert scores['accuracy']==(3000-len(errors))/3000
    write_csv(OUT/'per-class.csv',scores['per_class'])
    write_csv(OUT/'errors.csv',errors)
    fig,ax=plt.subplots(figsize=(7,6),layout='constrained')
    ax.imshow(cm,cmap='Blues'); ax.set(xticks=range(6),yticks=range(6),xticklabels=CLASSES,yticklabels=CLASSES,
        xlabel='Nhãn dự đoán',ylabel='Nhãn thật',title=f'{name} · epoch {best["epoch"]} · 3.000 ảnh test')
    for (i,j),n in np.ndenumerate(cm):
        ax.text(j,i,str(n),ha='center',va='center',color='white' if n>cm.max()/2 else 'black')
    fig.savefig(OUT/'confusion.png',dpi=155); plt.close(fig)
    pairs=Counter((r['truth'],r['predicted']) for r in errors)
    examples=[next(r for r in errors if (r['truth'],r['predicted'])==pair) for pair,_ in pairs.most_common(6)]
    fig,axes=plt.subplots(2,3,figsize=(9,6),layout='constrained')
    for ax,r in zip(axes.flat,examples):
        with Image.open(RAW/r['path']) as im: ax.imshow(im)
        ax.set_title(f"{r['truth']} → {r['predicted']}"); ax.axis('off')
    fig.savefig(OUT/'errors.png',dpi=145); plt.close(fig)
    lines=['# P04 · Đánh giá DenseNet121 trên Intel Image Classification','',
           f"Model chọn trước test: {name}, epoch {best['epoch']}. Validation sau reload: {check['accuracy']:.2%}, loss {check['loss']:.4f}.",
           f"Test: đúng {cm.trace()}/3000, sai {len(errors)}, accuracy {scores['accuracy']:.2%}, macro-F1 {scores['macro_f1']:.4f}, loss {loss_sum/3000:.4f}.",'',
           '| Lớp | Precision | Recall | F1 | Số ảnh |','|---|---:|---:|---:|---:|']
    for r in scores['per_class']:
        lines.append(f"| {r['name']} | {r['precision']:.2%} | {r['recall']:.2%} | {r['f1']:.2%} | {r['support']} |")
    lines+=['','![Ma trận nhầm lẫn](confusion.png)','',
            'Các hướng nhầm nhiều nhất (nhãn thật → dự đoán): '+', '.join(f'{a} → {b}: {n}' for (a,b),n in pairs.most_common(5))+'.','',
            '![Ví dụ lỗi, một ảnh cho mỗi hướng nhầm](errors.png)','',
            'Macro-F1 lấy trung bình F1 của sáu lớp. Loss là cross-entropy trung bình theo ảnh. Tập test đã từng được xem ở lần làm Lab trước. Kết quả mô tả một seed và bản chia hiện tại.']
    (OUT/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    saved=dict(status='PASSED',time=now(),version=version,validation=check,loss=loss_sum/len(disk),
               predictions_sha256=sha256(OUT/'predictions.csv'),**scores)
    write_json(cache,saved)
    return saved


if __name__=='__main__':
    print(run())
