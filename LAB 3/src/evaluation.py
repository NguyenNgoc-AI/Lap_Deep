"""EVALUATION — đánh giá model đã fine-tune trên tập TEST (chỉ dùng ở bước cuối).

Chạy:  python -m src.evaluation
  - So sánh với DistilBERT chưa fine-tune (baseline) trên cùng tập test.
  - Accuracy, Precision, Recall, F1 (thư viện `evaluate`), báo cáo theo lớp.
  - Lưu results/test_metrics.json, results/confusion_matrix.png,
    results/misclassified.csv (các câu bị dự đoán sai).
"""
import csv
import json
import os

import numpy as np
import torch
from sklearn.metrics import classification_report, confusion_matrix
from transformers import DataCollatorWithPadding, Trainer, TrainingArguments, set_seed

from src import config
from src.data import load_raw, tokenize
from src.model import load_classifier, load_finetuned, load_tokenizer


def predict(model, tokenizer, ds):
    """Trả về (logits, labels) trên tập đã tokenize."""
    args = TrainingArguments(output_dir=str(config.CHECKPOINT_DIR / "_eval"),
                             per_device_eval_batch_size=config.EVAL_BATCH_SIZE,
                             fp16=torch.cuda.is_available(), report_to="none")
    trainer = Trainer(model=model, args=args, processing_class=tokenizer,
                      data_collator=DataCollatorWithPadding(tokenizer=tokenizer))
    out = trainer.predict(ds)
    return out.predictions, out.label_ids


_EVALUATE_METRICS = None  # nạp một lần, dùng lại cho mọi lần tính


def _load_evaluate_metrics():
    """Nạp accuracy và F1 từ thư viện `evaluate` (đề yêu cầu) đúng một lần.

    Chỉ dùng bản đã lưu trên máy (HF_EVALUATE_OFFLINE=1), không hỏi Hugging Face Hub,
    để không bị treo chờ mạng. Bản lưu có sẵn sau khi chạy notebook ex2.
    Không nạp được thì trả về {} và dùng sklearn.
    """
    global _EVALUATE_METRICS
    if _EVALUATE_METRICS is None:
        os.environ.setdefault("HF_EVALUATE_OFFLINE", "1")
        try:
            import evaluate
            _EVALUATE_METRICS = {n: evaluate.load(n) for n in ("accuracy", "f1")}
            print("Accuracy, F1: thư viện evaluate (bản lưu trên máy). Precision, recall: sklearn.")
        except Exception as exc:
            print(f"(Không nạp được thư viện evaluate: {str(exc)[:120]}... Dùng sklearn cho mọi chỉ số.)")
            _EVALUATE_METRICS = {}
    return _EVALUATE_METRICS


def compute_metrics(preds, labels):
    """Accuracy, F1 bằng `evaluate` nếu có; precision, recall bằng sklearn."""
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    metrics = _load_evaluate_metrics()
    scores = {
        "precision": float(precision_score(labels, preds, zero_division=0)),
        "recall": float(recall_score(labels, preds, zero_division=0)),
    }
    if metrics:
        scores["accuracy"] = float(metrics["accuracy"].compute(predictions=preds, references=labels)["accuracy"])
        scores["f1"] = float(metrics["f1"].compute(predictions=preds, references=labels)["f1"])
    else:
        scores["accuracy"] = float(accuracy_score(labels, preds))
        scores["f1"] = float(f1_score(labels, preds, zero_division=0))
    return scores


def plot_confusion(cm, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    names = [config.ID2LABEL[i] for i in sorted(config.ID2LABEL)]
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(cm, cmap="Blues")
    fig.colorbar(im)
    ax.set_xticks(range(len(names)), names)
    ax.set_yticks(range(len(names)), names)
    ax.set_xlabel("Nhãn dự đoán"); ax.set_ylabel("Nhãn thật")
    ax.set_title("Confusion matrix trên tập test")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    config.ensure_dirs()
    raw = load_raw()
    tokenizer, model = load_finetuned()
    test_ds = tokenize(raw, tokenizer)["test"]
    texts = raw["test"]["text"]
    print(f"Tập test: {len(test_ds)} câu")

    # Baseline: DistilBERT gốc, lớp phân loại chưa được huấn luyện (cố định seed để tái lập)
    set_seed(config.SEED)
    base_logits, labels = predict(load_classifier(), load_tokenizer(), tokenize(raw, load_tokenizer())["test"])
    base = compute_metrics(np.argmax(base_logits, axis=-1), labels)

    logits, labels = predict(model, tokenizer, test_ds)
    preds = np.argmax(logits, axis=-1)
    probs = torch.softmax(torch.tensor(logits, dtype=torch.float32), dim=-1).numpy()
    metrics = compute_metrics(preds, labels)

    names = [config.ID2LABEL[i] for i in sorted(config.ID2LABEL)]
    report = classification_report(labels, preds, target_names=names, digits=4, output_dict=True)
    cm = confusion_matrix(labels, preds)

    print("\n              | Accuracy | Precision | Recall  | F1")
    for title, m in (("Chưa fine-tune", base), ("Đã fine-tune", metrics)):
        print(f"{title:13s} | {m['accuracy']:.2%}   | {m['precision']:.2%}    | {m['recall']:.2%}  | {m['f1']:.2%}")
    print("\n" + classification_report(labels, preds, target_names=names, digits=4))
    print("Confusion matrix (hàng = nhãn thật, cột = dự đoán):\n", cm)

    wrong = np.where(preds != labels)[0]
    with open(config.RESULTS_DIR / "misclassified.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "true_label", "predicted_label", "confidence"])
        for i in wrong:
            w.writerow([texts[i], names[labels[i]], names[preds[i]], f"{probs[i].max():.4f}"])

    result = {
        "model": str(config.FINETUNED_DIR.relative_to(config.ROOT)),
        "test_size": int(len(labels)),
        "baseline_not_finetuned": base,
        "finetuned": metrics,
        "per_class": {n: report[n] for n in names},
        "confusion_matrix": cm.tolist(),
        "num_misclassified": int(len(wrong)),
    }
    (config.RESULTS_DIR / "test_metrics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    plot_confusion(cm, config.RESULTS_DIR / "confusion_matrix.png")
    print(f"\nSố câu dự đoán sai: {len(wrong)} / {len(labels)}")
    print(f"Đã lưu: test_metrics.json, confusion_matrix.png, misclassified.csv trong {config.RESULTS_DIR}")
    print('Bước tiếp theo: python -m src.demo "your sentence here"')


if __name__ == "__main__":
    main()
