"""Summarize completed normal runs from disk, without using the test set."""
from pathlib import Path
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
report = json.loads((root/'report.json').read_text('utf8'))
assert report['status']=='PASSED' and report['smoke'] is False
lines=['# Huấn luyện trên bản chia theo nhóm cảnh','',
       'Mỗi epoch dùng 11.173 ảnh train và 2.793 ảnh validation. Test giữ cho bước đánh giá sau khi khóa lựa chọn.', '',
       '| Run | Epoch thực chạy | Epoch tốt nhất | Số đúng / 2.793 | Accuracy | Loss | Lý do dừng |',
       '|---|---:|---:|---:|---:|---:|---|']
for name in report['runs']:
    result=json.loads((root/name/'result.json').read_text('utf8'))
    rows=result['history']; best=result['best']; reload=result['validation_reload']
    assert reload['accuracy']==best['val_accuracy'] and math.isclose(reload['loss'],best['val_loss'],abs_tol=1e-5)
    assert all(r['train_samples']==11173 and r['val_samples']==2793 for r in rows)
    lines.append(f"| {name} | {len(rows)} | {best['epoch']} | {round(2793*reload['accuracy'])} | {100*reload['accuracy']:.2f}% | {reload['loss']:.4f} | {result['stop_reason']} |")
    fig,axes=plt.subplots(2,1,figsize=(8,6),sharex=True,layout='constrained')
    for ax,metric in zip(axes,['loss','accuracy']):
        for split in ['train','val']:
            ax.plot([r['epoch'] for r in rows],[r[f'{split}_{metric}'] for r in rows],marker='o',label=split)
        ax.axvline(best['epoch'],color='black',ls=':',label='Best epoch')
        if rows[0]['epoch']==1: ax.axvline(5.5,color='gray',ls='--',label='Chuyển stage')
        ax.set_ylabel(metric); ax.legend(); ax.grid(alpha=.2)
    axes[-1].set_xlabel('Epoch');fig.suptitle(name)
    fig.savefig(root/name/'curves.png',dpi=140);plt.close(fig)
lines+=['',f"Chọn **{report['selected_by_validation']}** bằng validation trong hai run chính. Nhánh VGG LR thấp chỉ dùng phân tích.",'']
lines += [f'![{n}]({n}/curves.png)' for n in report['runs']]
(root/'TRAINING.md').write_text('\n'.join(lines)+'\n', encoding='utf8')
