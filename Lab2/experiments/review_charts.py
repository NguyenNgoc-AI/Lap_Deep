from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/pipeline_16_steps/review_charts'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def show(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, dpi=160, bbox_inches='tight')
    display(fig)
    plt.close(fig)


def transfer():
    runs = [read(f'outputs/experiments/R{i:02d}/result.json') for i in range(1, 7)]
    fig, ax = plt.subplots(figsize=(11, 5), layout='constrained')
    for i, r in enumerate(runs):
        value = 100 * r['best']['val_accuracy']
        ax.scatter(value, i, s=90, color='#2378b5' if r['spec']['model'] == 'vgg11' else '#8b55ad')
        ax.annotate(f"{value:.2f}% / epoch {r['best']['epoch']}", (value, i), xytext=(8, 0),
                    textcoords='offset points', va='center', fontsize=9)
    ax.set(yticks=range(6), yticklabels=[f"{r['id']} | {r['spec']['model']} | lr={r['spec']['lr']} | B{r['spec']['batch']}" for r in runs],
           xlim=(90, 92.3), xlabel='Best validation accuracy (%) — zoomed axis',
           title='Transfer learning only | R01–R06 | 5 epochs each / seed 42')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=.2)
    show(fig, 'transfer_comparison.png')


def evaluation():
    result = read('outputs/report/R07_test.json')
    cm = np.asarray(result['confusion_matrix'])
    classes = [r['name'] for r in result['per_class']]
    supports = cm.sum(axis=1)
    norm = cm / supports[:, None] * 100
    assert cm.sum() == result['samples'] == 3000
    assert np.isclose(cm.trace() / cm.sum(), result['accuracy'])
    assert np.allclose(norm.sum(axis=1), 100)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), layout='constrained')
    for ax, values, title in zip(axes, (cm, norm), ('Counts', 'Row-normalized (%)')):
        im = ax.imshow(values, cmap='Blues', vmin=0, vmax=100 if title.endswith('(%)') else cm.max())
        for i in range(6):
            for j in range(6):
                ax.text(j, i, str(cm[i, j]) if title == 'Counts' else f'{values[i,j]:.1f}%',
                        ha='center', va='center', fontsize=9,
                        color='white' if values[i,j] > im.norm.vmax * .55 else 'black')
        ax.set(xticks=range(6), xticklabels=classes, yticks=range(6),
               yticklabels=[f'{c} (n={s})' for c, s in zip(classes, supports)],
               xlabel='Predicted label', ylabel='True label', title=title)
        ax.tick_params(axis='x', rotation=35)
        fig.colorbar(im, ax=ax, shrink=.75)
    fig.suptitle('R07 original | checkpoint epoch 3 | Test n=3000 | Accuracy 92.80%')
    show(fig, 'R07_confusion_counts_percent.png')
    precision = np.divide(cm.diagonal(), cm.sum(axis=0), out=np.zeros(6), where=cm.sum(axis=0) != 0)
    recall = cm.diagonal() / supports
    f1 = 2 * precision * recall / (precision + recall)
    assert np.allclose(f1, [r['f1'] for r in result['per_class']])
    fig, ax = plt.subplots(figsize=(11, 5), layout='constrained')
    x = np.arange(6)
    for offset, values, label, color in [(-.25, precision, 'Precision', '#2378b5'),
                                        (0, recall, 'Recall', '#d65b24'), (.25, f1, 'F1', '#489963')]:
        bars = ax.bar(x + offset, values * 100, width=.24, label=label, color=color)
        ax.bar_label(bars, fmt='%.1f', fontsize=8)
    ax.set(xticks=x, xticklabels=[f'{c}\nn={s}' for c, s in zip(classes, supports)],
           ylim=(0, 110), yticks=range(0, 101, 20), ylabel='Score (%)',
           title='R07 original | checkpoint epoch 3 | Per-class test metrics')
    ax.legend(loc='lower right')
    ax.grid(axis='y', alpha=.2)
    show(fig, 'R07_per_class.png')


if __name__ == '__main__':
    transfer()
    evaluation()
