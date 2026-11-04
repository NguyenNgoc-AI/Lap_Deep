"""TRAINING — fine-tune DistilBERT cho phân loại cảm xúc 2 lớp bằng Trainer.

Chạy:  python -m src.train
  - Theo dõi trên tập VALIDATION sau mỗi epoch (không dùng test để chọn model).
  - Giữ lại epoch có validation accuracy cao nhất (load_best_model_at_end).
  - Lưu model tốt nhất vào models/distilbert-rotten-tomatoes/.
  - Lưu nhật ký huấn luyện results/train_log.json, results/train_history.csv
    và biểu đồ results/loss_curve.png.
Máy chỉ có CPU: đặt biến môi trường LAB3_TRAIN_LIMIT=2000 để train nhanh hơn.
"""
import csv
import json
import math
import shutil
import time

import numpy as np
import torch
from transformers import DataCollatorWithPadding, Trainer, TrainingArguments, set_seed

from src import config
from src.data import load_raw, tokenize
from src.model import count_parameters, load_classifier, load_tokenizer


def accuracy_f1(eval_pred):
    """Metric cho Trainer: accuracy và F1 (lớp POSITIVE)."""
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    tp = int(((preds == 1) & (labels == 1)).sum())
    fp = int(((preds == 1) & (labels == 0)).sum())
    fn = int(((preds == 0) & (labels == 1)).sum())
    f1 = 2 * tp / max(2 * tp + fp + fn, 1)
    return {"accuracy": float((preds == labels).mean()), "f1": f1}


def build_trainer(train_ds, val_ds, tokenizer, model):
    steps_per_epoch = math.ceil(len(train_ds) / config.TRAIN_BATCH_SIZE)
    logging_steps = max(1, min(config.LOGGING_STEPS, steps_per_epoch // 5))  # ≥ 5 lần log mỗi epoch
    args = TrainingArguments(
        output_dir=str(config.CHECKPOINT_DIR),
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,       # giữ epoch tốt nhất trên validation
        metric_for_best_model="accuracy",
        greater_is_better=True,
        save_total_limit=2,
        learning_rate=config.LEARNING_RATE,
        per_device_train_batch_size=config.TRAIN_BATCH_SIZE,
        per_device_eval_batch_size=config.EVAL_BATCH_SIZE,
        num_train_epochs=config.NUM_EPOCHS,
        weight_decay=config.WEIGHT_DECAY,
        logging_steps=logging_steps,
        fp16=torch.cuda.is_available(),
        report_to="none",
        seed=config.SEED,
    )
    return Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=accuracy_f1,
    )


def epoch_table(log_history):
    """Gộp log thành bảng theo epoch: train loss (trung bình các lần log) và validation."""
    rows = {}
    for entry in log_history:
        ep = entry.get("epoch")
        if ep is None:
            continue
        key = int(round(ep)) if "eval_loss" in entry else int(np.ceil(ep))
        row = rows.setdefault(key, {"epoch": key, "train_losses": []})
        if "loss" in entry:
            row["train_losses"].append(entry["loss"])
        if "eval_loss" in entry:
            row.update(val_loss=entry["eval_loss"], val_accuracy=entry["eval_accuracy"],
                       val_f1=entry["eval_f1"])
    table = []
    for key in sorted(rows):
        r = rows[key]
        if "val_loss" not in r:
            continue
        losses = r.pop("train_losses")
        r["train_loss"] = float(np.mean(losses)) if losses else None
        table.append(r)
    return table


def plot_loss(log_history, table, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    steps = [e["step"] for e in log_history if "loss" in e]
    losses = [e["loss"] for e in log_history if "loss" in e]
    eval_steps = [e["step"] for e in log_history if "eval_loss" in e]
    eval_losses = [e["eval_loss"] for e in log_history if "eval_loss" in e]

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(steps, losses, marker="o", markersize=3, label="Training loss")
    axes[0].plot(eval_steps, eval_losses, marker="s", label="Validation loss")
    axes[0].set_xlabel("Step"); axes[0].set_ylabel("Loss")
    axes[0].set_title("Loss khi fine-tune"); axes[0].grid(True, alpha=0.3); axes[0].legend()

    epochs = [r["epoch"] for r in table]
    axes[1].plot(epochs, [r["val_accuracy"] for r in table], marker="o", label="Validation accuracy")
    axes[1].plot(epochs, [r["val_f1"] for r in table], marker="s", label="Validation F1")
    axes[1].set_xlabel("Epoch"); axes[1].set_xticks(epochs)
    axes[1].set_title("Validation accuracy / F1 theo epoch"); axes[1].grid(True, alpha=0.3); axes[1].legend()
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    config.ensure_dirs()
    set_seed(config.SEED)
    device = "GPU " + torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print("Thiết bị:", device)

    tokenizer = load_tokenizer()
    ds = tokenize(load_raw(), tokenizer)
    train_ds = ds["train"].shuffle(seed=config.SEED)
    if config.TRAIN_LIMIT:
        train_ds = train_ds.select(range(min(config.TRAIN_LIMIT, len(train_ds))))
    val_ds = ds["validation"]
    print(f"Train: {len(train_ds)} câu | Validation: {len(val_ds)} câu")

    model = load_classifier()
    total, trainable = count_parameters(model)
    print(f"Model: {config.BASE_MODEL} | {total:,} tham số ({trainable:,} huấn luyện được)")

    trainer = build_trainer(train_ds, val_ds, tokenizer, model)
    before = trainer.evaluate()
    print(f"Validation TRƯỚC fine-tune: accuracy = {before['eval_accuracy']:.2%}, loss = {before['eval_loss']:.4f}")

    start = time.time()
    trainer.train()
    minutes = (time.time() - start) / 60

    table = epoch_table(trainer.state.log_history)
    best = max(table, key=lambda r: r["val_accuracy"])
    print("\nEpoch | Train loss | Val loss | Val acc | Val F1")
    for r in table:
        mark = "  <- tốt nhất" if r is best else ""
        train_loss = f"{r['train_loss']:.4f}" if r["train_loss"] is not None else "   -  "
        print(f"{r['epoch']:5d} | {train_loss}     | {r['val_loss']:.4f}   | "
              f"{r['val_accuracy']:.2%} | {r['val_f1']:.2%}{mark}")

    # Lưu model tốt nhất (Trainer đã nạp lại epoch tốt nhất)
    if config.FINETUNED_DIR.exists():
        shutil.rmtree(config.FINETUNED_DIR)
    trainer.save_model(str(config.FINETUNED_DIR))
    tokenizer.save_pretrained(str(config.FINETUNED_DIR))

    log = {
        "device": device,
        "base_model": config.BASE_MODEL,
        "dataset": config.DATASET_NAME,
        "train_size": len(train_ds),
        "validation_size": len(val_ds),
        "hyperparameters": {
            "learning_rate": config.LEARNING_RATE, "train_batch_size": config.TRAIN_BATCH_SIZE,
            "num_epochs": config.NUM_EPOCHS, "weight_decay": config.WEIGHT_DECAY,
            "max_length": config.MAX_LENGTH, "seed": config.SEED, "fp16": torch.cuda.is_available(),
        },
        "train_minutes": round(minutes, 2),
        "validation_before_finetune": {"accuracy": before["eval_accuracy"], "loss": before["eval_loss"]},
        "epochs": table,
        "best_epoch": best["epoch"],
        "log_history": trainer.state.log_history,
    }
    (config.RESULTS_DIR / "train_log.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(config.RESULTS_DIR / "train_history.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["epoch", "train_loss", "val_loss", "val_accuracy", "val_f1"])
        w.writeheader()
        for r in table:
            w.writerow({k: r[k] for k in w.fieldnames})
    plot_loss(trainer.state.log_history, table, config.RESULTS_DIR / "loss_curve.png")

    print(f"\nHuấn luyện xong trong {minutes:.1f} phút. Epoch tốt nhất: {best['epoch']}")
    print(f"Model đã lưu: {config.FINETUNED_DIR}")
    print(f"Nhật ký: {config.RESULTS_DIR / 'train_log.json'}, biểu đồ: {config.RESULTS_DIR / 'loss_curve.png'}")
    print("Bước tiếp theo: python -m src.evaluation")


if __name__ == "__main__":
    main()
