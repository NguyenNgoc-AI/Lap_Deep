"""EVALUATION — đánh giá model đã fine-tune trên tập TEST (chỉ dùng ở bước cuối).

Chạy:  python -m src.evaluation
  - So sánh với DistilBERT chưa fine-tune (baseline) trên cùng tập test.
  - Accuracy, Precision, Recall, F1 (thư viện `evaluate`), báo cáo theo lớp.
  - Lưu results/test_metrics.json, results/confusion_matrix.png,
    results/misclassified.csv (các câu bị dự đoán sai).
"""
import csv
import json

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


def compute_metrics(preds, labels):
    """Dùng thư viện `evaluate` như đề yêu cầu; nếu không tải được metric thì dùng sklearn."""
    try:
        import evaluate
        scores = {}
        for name in ("accuracy", "precision", "recall", "f1"):
            scores.update(evaluate.load(name).compute(predictions=preds, references=labels))
        return {k: float(v) for k, v in scores.items()}
    except Exception as exc:  # không có mạng lần đầu, v.v.
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        print(f"(Không dùng được thư viện evaluate: {exc}. Dùng sklearn thay thế.)")
        return {"accuracy": accuracy_score(labels, preds), "precision": precision_score(labels, preds),
                "recall": recall_score(labels, preds), "f1": f1_score(labels, preds)}


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
