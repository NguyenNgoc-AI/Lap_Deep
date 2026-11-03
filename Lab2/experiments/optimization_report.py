from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import Markdown, display

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/optimization_v1'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def run():
    summary = read(OUT / 'summary.json')
    assert summary['status'] == 'COMPLETED' and not summary['test_evaluated']
    original = read(ROOT / 'outputs/experiments/R07/result.json')['best']
    extended = read(ROOT / 'outputs/experiments/R07_5epochs/result.json')['best']
    rows = [('R07 original', original), ('R07_5epochs', extended)]
    rows += [(r['run'], r['selected']) for r in summary['results']]
    text = ['### Tối ưu trên development — kết quả thực nghiệm', '',
            'Hai run mới cùng khởi tạo từ R02, AdamW learning rate 3e-6, batch 8, seed 42. '
            'R08 có weight decay 0; R09 có weight decay 0,01. '
            'Đây là phân tích thăm dò sau khi đã xem test gốc; không có test mới.', '',
            '| Run | Epoch được chọn | Validation accuracy | Validation loss |',
            '|---|---:|---:|---:|']
    for name, row in rows:
        text.append(f"| {name} | {row['epoch']} | {100*row['val_accuracy']:.4f}% | {row['val_loss']:.6f} |")
    selected = summary['selected']
    delta_acc = 100 * (selected['val_accuracy'] - extended['val_accuracy'])
    delta_loss = selected['val_loss'] - extended['val_loss']
    text += ['', f"Ứng viên được chọn trong lượt mới: **{summary['winner']} / epoch {selected['epoch']}**. "
             f"So với R07_5epochs epoch 5: accuracy thay đổi **{delta_acc:+.4f} điểm phần trăm**, "
             f"loss thay đổi **{delta_loss:+.6f}**.", '',
             'Quy tắc chốt trước chạy: chọn accuracy cao nhất trong các checkpoint có loss không vượt '
             'checkpoint khởi tạo; nếu hòa, chọn loss thấp hơn rồi epoch sớm hơn. '
             'Early stopping theo validation loss, patience 2 và min_delta 1e-4; '
             'epoch 0 là đánh giá R02 trước fine-tuning, không phải một epoch training.', '',
             '| Run | Epoch đã train | Lý do dừng | Epoch min-loss | Min-loss | Epoch max-accuracy | Max-accuracy |',
             '|---|---:|---|---:|---:|---:|---:|']
    for r in summary['results']:
        text.append(f"| {r['run']} | {len(r['history'])-1} | {r['stop_reason']} | {r['best_loss']['epoch']} | "
                    f"{r['best_loss']['val_loss']:.6f} | {r['best_accuracy']['epoch']} | {100*r['best_accuracy']['val_accuracy']:.4f}% |")
    text += ['', 'Các run mới chỉ khác weight decay nên có thể dùng để khảo sát hiệu ứng này trong một seed. '
             'So với R07 còn thay đổi LR/optimizer/quy tắc dừng và lựa chọn, không quy mọi chênh lệch cho weight decay. '
             'Không suy ra độ ổn định nhiều seed, tính calibration hoặc test accuracy từ kết quả validation.', '',
             f"Checkpoint đề xuất: `outputs/optimization_v1/{summary['winner']}/best.pt`. "
             'Model inference và kết quả test cũ vẫn thuộc R07 epoch 3; không tự gán chúng cho ứng viên mới.']
    if delta_acc <= 0 or delta_loss >= 0:
        text += ['', '**Chưa có cải thiện đồng thời accuracy và loss so với R07_5epochs.** '
                 'Ứng viên được chọn theo ràng buộc loss của thí nghiệm mới không đồng nghĩa tốt hơn về mọi chỉ số. '
                 'Giữ R07 gốc làm model đã có đánh giá test; không tự thay model chỉ vì loss thấp hơn.']
    else:
        text += ['', '**Cả accuracy và loss validation đều cải thiện trong seed này**, '
                 'nhưng chưa có kiểm chứng đa seed hoặc test độc lập cho ứng viên mới.']
    report = '\n'.join(text)
    (OUT / 'analysis.md').write_text(report, encoding='utf-8')
    display(Markdown(report))
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), layout='constrained')
    for column, r in enumerate(summary['results']):
        history = r['history']
        for line, metric, scale in [(0, 'loss', 1), (1, 'accuracy', 100)]:
            ax = axes[line, column]
            ax.plot([v['epoch'] for v in history], [scale*v['val_'+metric] for v in history],
                    '--o', color='#d65b24', label='Validation: center crop')
            trained = history[1:]
            ax.plot([v['epoch'] for v in trained], [scale*v['train_'+metric] for v in trained],
                    '-o', color='#2378b5', label='Train: augmented / online')
            best = r['selected']
            ax.scatter(best['epoch'], scale*best['val_'+metric], marker='D', s=80, color='black',
                       zorder=4, label='Selected: accuracy with loss constraint')
            minimum = r['best_loss']
            ax.scatter(minimum['epoch'], scale*minimum['val_'+metric], marker='*', s=160,
                       facecolors='none', edgecolors='#489963', linewidths=2, zorder=5, label='Minimum validation loss')
            ax.set(title=f"{r['run']} | weight decay={r['weight_decay']} | {metric}",
                   xlabel='Fine-tuning epoch (0 = initial R02)', ylabel='Accuracy (%)' if metric=='accuracy' else 'Cross-entropy',
                   xticks=range(6), xlim=(-.2, 5.3))
            if metric == 'accuracy':
                ax.set_ylim(90, 100)
            else:
                ax.set_ylim(0, .31)
            ax.grid(alpha=.2)
            if line == 0:
                ax.legend(fontsize=8)
    fig.suptitle('Optimization v1 | Development only | Seed 42 | New checkpoints NOT tested')
    fig.savefig(OUT / 'learning_curves.png', dpi=160)
    display(fig)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout='constrained')
    for ax, metric, scale, label in zip(axes, ['val_accuracy', 'val_loss'], [100, 1], ['Validation accuracy (%)', 'Validation loss']):
        values = [r[metric]*scale for _, r in rows]
        ax.scatter(values, np.arange(len(rows)), s=70)
        for i, value in enumerate(values):
            ax.annotate(f'{value:.4f}', (value, i), xytext=(8, 0), textcoords='offset points', va='center')
        ax.set(yticks=range(len(rows)), yticklabels=[f"{name} / ep{r['epoch']}" for name,r in rows], xlabel=label)
        ax.margins(x=.45, y=.2)
        ax.invert_yaxis()
        ax.grid(axis='x', alpha=.2)
    fig.suptitle('Selected checkpoints | Validation only | Different selection rules noted in table')
    fig.savefig(OUT / 'checkpoint_comparison.png', dpi=160)
    display(fig)
    plt.close(fig)


if __name__ == '__main__':
    run()
