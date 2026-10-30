"""One held-out evaluation per selected checkpoint and evidence-based local report."""
import csv
import gc
import os

import numpy as np
import torch

from src.common import ROOT, now, read_json, sha256, write_json
from src.phases.phase_02_data import CLASSES, loader
from src.phases.phase_03_models import build
from src.phases.phase_04_train import OUT as RUNS, fingerprint, provenance

OUT = ROOT / 'outputs/report'


def metrics(confusion):
    cm = np.asarray(confusion, dtype=np.int64)
    if cm.shape != (6, 6) or (cm < 0).any() or not cm.sum():
        raise ValueError('Invalid confusion matrix')
    tp = cm.diagonal().astype(float)
    support, predicted = cm.sum(axis=1), cm.sum(axis=0)
    precision = np.divide(tp, predicted, out=np.zeros(6), where=predicted != 0)
    recall = np.divide(tp, support, out=np.zeros(6), where=support != 0)
    f1 = np.divide(2 * precision * recall, precision + recall, out=np.zeros(6), where=(precision + recall) != 0)
    return {'accuracy': float(tp.sum() / cm.sum()), 'macro_f1': float(f1.mean()),
            'samples': int(cm.sum()), 'confusion_matrix': cm.tolist(),
            'per_class': [dict(name=name, precision=float(precision[i]), recall=float(recall[i]),
                               f1=float(f1[i]), support=int(support[i])) for i, name in enumerate(CLASSES)]}


def evaluate(run_id, device):
    result = read_json(RUNS / run_id / 'result.json')
    path = RUNS / run_id / 'best.pt'
    checksum = sha256(path)
    if checksum != result['checkpoint_hashes']['best.pt']:
        raise ValueError('Test checkpoint was modified')
    cache = OUT / f'{run_id}_test.json'
    predictions_path = OUT / f'{run_id}_predictions.csv'
    if cache.exists():
        saved = read_json(cache)
        if saved['checkpoint_sha256'] != checksum or saved['predictions_sha256'] != sha256(predictions_path):
            raise ValueError('Stale test artifacts')
        return saved
    model = build(result['spec']['model'], result['spec']['mode']).to(device)
    checkpoint = torch.load(path, map_location='cpu', weights_only=False)
    model.load_state_dict(checkpoint['model'])
    del checkpoint
    model.eval()
    batches = loader('test', result['spec']['batch'])
    confusion = np.zeros((6, 6), dtype=np.int64)
    predictions, total_loss, offset = [], 0., 0
    with torch.no_grad():
        for images, labels in batches:
            logits = model(images.to(device))
            loss = torch.nn.functional.cross_entropy(logits, labels.to(device), reduction='sum')
            if not torch.isfinite(loss).item():
                raise FloatingPointError('Non-finite test loss')
            total_loss += loss.item()
            predicted = logits.argmax(1).cpu().tolist()
            for truth, prediction in zip(labels.tolist(), predicted):
                confusion[truth, prediction] += 1
                predictions.append({'relative_path': batches.dataset.rows[offset]['relative_path'],
                                    'truth': truth, 'prediction': prediction})
                offset += 1
    if offset != len(batches.dataset):
        raise ValueError('Test sample count mismatch')
    write_csv(predictions_path, predictions)
    saved = {'run': run_id, 'checkpoint_sha256': checksum, 'evaluated': now(),
             'predictions_sha256': sha256(predictions_path), 'loss': total_loss / offset,
             **metrics(confusion)}
    write_json(cache, saved)
    del model, batches
    gc.collect()
    if device == 'xpu':
        torch.xpu.empty_cache()
    print(f'{run_id} test: accuracy={saved["accuracy"]:.4f}, macro-F1={saved["macro_f1"]:.4f}', flush=True)
    return saved


def write_csv(path, rows):
    temporary = path.with_suffix('.csv.tmp')
    with temporary.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def charts(results, evaluations):
    os.environ.setdefault('MPLCONFIGDIR', str(ROOT / 'outputs/matplotlib-cache'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for result in results:
        rows = result['history']
        for ax, key in zip(axes.flat, ['train_loss', 'val_loss', 'train_accuracy', 'val_accuracy']):
            ax.plot([r['epoch'] for r in rows], [r[key] for r in rows], marker='o', label=result['id'])
            ax.set(xlabel='Epoch within run', ylabel=key.replace('_', ' '))
            ax.grid(alpha=.2)
    axes[0, 0].legend(ncol=2)
    fig.suptitle('Intel scenes: transfer runs R01–R06; R07 starts from the winning checkpoint')
    fig.savefig(OUT / 'learning_curves.png', dpi=160)
    plt.close(fig)
    for evaluation in evaluations:
        cm = np.array(evaluation['confusion_matrix'])
        fig, ax = plt.subplots(figsize=(8, 7), constrained_layout=True)
        plot = ax.imshow(cm, cmap='Blues')
        fig.colorbar(plot, ax=ax)
        ax.set(xticks=range(6), yticks=range(6), xticklabels=CLASSES, yticklabels=CLASSES,
               xlabel='Predicted', ylabel='True', title=f'{evaluation["run"]} — test confusion matrix (counts)')
        plt.setp(ax.get_xticklabels(), rotation=35, ha='right')
        for i in range(6):
            for j in range(6):
                ax.text(j, i, str(cm[i, j]), ha='center', va='center',
                        color='white' if cm[i, j] > cm.max()/2 else 'black')
        fig.savefig(OUT / f'{evaluation["run"]}_confusion_matrix.png', dpi=160)
        plt.close(fig)


def report(results, evaluations, selection):
    audit = read_json(ROOT / 'outputs/data/audit.json')
    preflight = read_json(ROOT / 'outputs/models/preflight.json')
    counts = {s: sum(c.values()) for s, c in audit['counts'].items()}
    summary = []
    for r in results:
        summary.append({'run': r['id'], 'model': r['spec']['model'], 'mode': r['spec']['mode'],
                        'lr': r['spec']['lr'], 'batch': r['spec']['batch'], 'epochs': r['spec']['epochs'],
                        'best_epoch': r['best']['epoch'], 'val_accuracy': r['best']['val_accuracy'],
                        'val_loss': r['best']['val_loss'], 'train_validation_seconds': r['seconds']})
    write_csv(OUT / 'experiments.csv', summary)
    write_csv(OUT / 'epoch_metrics.csv', [row for r in results for row in r['history']])
    write_csv(OUT / 'test_metrics.csv', [{'run': e['run'], 'accuracy': e['accuracy'], 'macro_f1': e['macro_f1'], 'loss': e['loss'], 'samples': e['samples']} for e in evaluations])
    write_csv(OUT / 'per_class_metrics.csv', [{'run': e['run'], **r} for e in evaluations for r in e['per_class']])
    lines = ['# Practice 2 — Pretrained neural networks: Intel Image Classification', '',
             f'Hoàn tất: {now()}. Thiết bị của toàn bộ ma trận: **{preflight["device"]}**.', '',
             '## Dữ liệu và phương pháp', '',
             f'Dataset Kaggle Intel Image Classification v2: {audit["original_train"]} ảnh train gốc, {audit["original_test"]} ảnh test và {audit["prediction_images"]} ảnh chưa gán nhãn (không dùng chấm điểm).',
             f'Sau kiểm tra SHA256/nhãn: train **{counts["train"]}**, validation **{counts["validation"]}**, test **{counts["test"]}**. Loại {len(audit["removed_train_duplicates"])} bản ghi train do trùng, chồng lấn test hoặc nhãn mâu thuẫn; không sửa dữ liệu gốc.',
             '13 nhóm ảnh có nhãn mâu thuẫn: cách ly 23 ảnh train; giữ nguyên test. Xem `../data/label_conflicts.json` và amendment 01. Train/validation/test không giao SHA256. Chia phân tầng seed 42, validation 20% làm tròn xuống theo lớp.',
             'Ảnh RGB được resize cạnh ngắn 256, crop 224 và chuẩn hóa ImageNet. Train dùng random crop/flip; validation/test dùng center crop. Adam, float32, num_workers=0, không bỏ batch cuối.',
             'Trọng số ImageNet1K_V1 của torchvision; thay đầu ra bằng 6 lớp. Transfer chỉ cập nhật linear cuối. Fine-tune mở block cuối cùng và linear cuối. Giữ dropout/BatchNorm ở eval trong mọi run để backbone cố định đúng nghĩa; affine của BN trong block mở vẫn nhận gradient.',
             'R01–R06: 5 epoch từ cùng weights và seed 42; mỗi cặp LR/batch chỉ thay một yếu tố. R07: 3 epoch bổ sung từ checkpoint validation tốt nhất, Adam mới lr 1e-5. Lựa chọn theo accuracy validation giảm dần, rồi loss, epoch và run ID tăng dần.', '',
             '## Kiến trúc', '', '| Model / mode | Tổng tham số | Trainable |', '|---|---:|---:|']
    for r in preflight['records']:
        if r['batch'] == 8:
            lines.append(f'| {r["model"]} / {r["mode"]} | {r["parameters_total"]:,} | {r["parameters_trainable"]:,} |')
    lines += ['', 'Cấu trúc đầy đủ và tên các tham số trainable: `../models/`.', '',
              '## Thí nghiệm validation', '', '| Run | Model | Mode | LR | Batch | Best epoch | Val accuracy | Val loss | Phút train+val |', '|---|---|---|---:|---:|---:|---:|---:|---:|']
    for r in summary:
        lines.append(f'| {r["run"]} | {r["model"]} | {r["mode"]} | {r["lr"]:g} | {r["batch"]} | {r["best_epoch"]} | {r["val_accuracy"]:.2%} | {r["val_loss"]:.4f} | {r["train_validation_seconds"]/60:.1f} |')
    lines += ['', '![Learning curves](learning_curves.png)', '', '## Nhận xét từ số đo', '']
    by_id = {r['id']: r for r in results}
    for base, lower, larger in [('R01', 'R02', 'R03'), ('R04', 'R05', 'R06')]:
        accuracy = lambda k: by_id[k]['best']['val_accuracy']
        lines.append(f'- {by_id[base]["spec"]["model"]}: giảm LR 0.001 → 0.0003 thay đổi validation accuracy {(accuracy(lower)-accuracy(base))*100:+.2f} điểm phần trăm; tăng batch 8 → 16 thay đổi {(accuracy(larger)-accuracy(base))*100:+.2f} điểm phần trăm (so với {base}).')
    parent = selection['best_transfer']
    delta = (by_id['R07']['best']['val_accuracy'] - by_id[parent]['best']['val_accuracy'])*100
    lines += [f'- Fine-tune R07 so với checkpoint cha {parent}: {delta:+.2f} điểm phần trăm validation. R07 có thêm ngân sách 3 epoch nên đây không phải so sánh ngang ngân sách.',
              f'- Model cuối được chốt bằng validation trước khi test: **{selection["final_run"]}**; best transfer: **{parent}**.', '',
              '## Đánh giá test sau khi khóa lựa chọn', '', '| Run | Test accuracy | Macro-F1 | Loss | Số ảnh |', '|---|---:|---:|---:|---:|']
    for e in evaluations:
        lines.append(f'| {e["run"]} | {e["accuracy"]:.2%} | {e["macro_f1"]:.4f} | {e["loss"]:.4f} | {e["samples"]} |')
    for e in evaluations:
        lines += ['', f'![{e["run"]} confusion matrix]({e["run"]}_confusion_matrix.png)']
    lines += ['', 'Precision, recall, F1 và support từng lớp trong `per_class_metrics.csv`; zero division = 0. Dự đoán từng ảnh nằm trong các file `*_predictions.csv`.', '',
              '## Giới hạn và khả năng tái lập', '',
              '- Chỉ một seed, chưa đo độ biến thiên qua nhiều lần chạy. Không suy rộng chênh lệch nhỏ thành kết luận thống kê.',
              '- Dataset có nhãn mơ hồ và ảnh trùng. SHA256 chỉ phát hiện trùng byte, không phát hiện tất cả ảnh gần giống.',
              '- Thời gian đo trên laptop Intel Arc dùng bộ nhớ chung; chịu ảnh hưởng nhiệt độ và tiến trình khác. Thời gian trong bảng chỉ gồm vòng train/validation, không gồm tải, khởi tạo hay ghi checkpoint.',
              '- XPU không được cam kết tái lập bitwise. Checkpoint lưu RNG, optimizer, config, source/data/dependency hashes để resume cùng môi trường.',
              '- Test không dùng điều chỉnh siêu tham số; model cuối không chọn theo test accuracy.', '',
              '## Artifacts', '', '`experiments.csv`, `epoch_metrics.csv`, `test_metrics.csv`, `per_class_metrics.csv`, `summary.json`; checkpoint/TensorBoard/identity theo từng run trong `../experiments/`.',
              'Nguồn dataset: https://www.kaggle.com/datasets/puneet6060/intel-image-classification/data. Weight provenance: `../models/weights.json`.']
    (OUT / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    write_json(OUT / 'summary.json', {'status': 'COMPLETED', 'created': now(), 'selection': selection,
                                     'data_counts': counts, 'experiments': summary, 'test': evaluations})


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    selection = read_json(RUNS / 'selection.json')
    if selection['provenance_hash'] != fingerprint(provenance()):
        raise ValueError('Source/data/dependencies changed after selection')
    results = [read_json(RUNS / f'R{i:02d}' / 'result.json') for i in range(1, 8)]
    if any(r['status'] != 'COMPLETED' for r in results):
        raise ValueError('Incomplete experiment matrix')
    evaluations = [evaluate(run_id, results[0]['device']) for run_id in selection['test_runs']]
    charts(results, evaluations)
    report(results, evaluations, selection)
    return read_json(OUT / 'summary.json')


if __name__ == '__main__':
    run()
