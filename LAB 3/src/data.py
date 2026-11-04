"""DATA — tải, mô tả, xuất CSV và tokenize bộ dữ liệu rotten_tomatoes.

Chạy:  python -m src.data
  - Tải dữ liệu từ Hugging Face Hub (lần đầu cần mạng).
  - In và lưu thống kê vào results/dataset_stats.json.
  - Xuất 3 tập train/validation/test ra data/rotten_tomatoes/*.csv.
Sau khi đã có CSV, các bước sau đọc thẳng từ CSV, không cần mạng.
"""
import json

from datasets import ClassLabel, DatasetDict, load_dataset

from src import config

SPLITS = ("train", "validation", "test")


def load_raw(prefer_local=True):
    """Trả về DatasetDict gồm train/validation/test, mỗi mẫu có `text` và `label`."""
    csv_files = {s: str(config.DATASET_CSV_DIR / f"{s}.csv") for s in SPLITS}
    if prefer_local and all((config.DATASET_CSV_DIR / f"{s}.csv").exists() for s in SPLITS):
        ds = load_dataset("csv", data_files=csv_files)
        print(f"Đọc dữ liệu từ CSV: {config.DATASET_CSV_DIR}")
    else:
        ds = load_dataset(config.DATASET_NAME)
        print(f"Tải dữ liệu từ Hugging Face Hub: {config.DATASET_NAME}")
    ds = DatasetDict({s: ds[s] for s in SPLITS})
    if not isinstance(ds["train"].features["label"], ClassLabel):
        ds = ds.cast_column("label", ClassLabel(names=["neg", "pos"]))  # 0 = neg, 1 = pos
    return ds


def describe(ds):
    """Thống kê số câu, phân bố nhãn và độ dài câu của từng tập."""
    names = ds["train"].features["label"].names
    stats = {"dataset": config.DATASET_NAME, "label_names": names, "splits": {}}
    for split in SPLITS:
        labels = ds[split]["label"]
        lengths = [len(t.split()) for t in ds[split]["text"]]
        stats["splits"][split] = {
            "num_rows": len(labels),
            "label_counts": {names[i]: labels.count(i) for i in range(len(names))},
            "avg_words": round(sum(lengths) / len(lengths), 1),
            "max_words": max(lengths),
        }
    return stats


def export_csv(ds):
    config.DATASET_CSV_DIR.mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        ds[split].to_csv(str(config.DATASET_CSV_DIR / f"{split}.csv"), index=False)


def tokenize(ds, tokenizer, max_length=config.MAX_LENGTH):
    """Tokenize cột `text`; padding để DataCollatorWithPadding làm theo từng batch."""
    def _tok(batch):
        return tokenizer(batch["text"], truncation=True, max_length=max_length)
    return ds.map(_tok, batched=True)


def main():
    config.ensure_dirs()
    ds = load_raw(prefer_local=False)
    print(ds)
    stats = describe(ds)
    for split, s in stats["splits"].items():
        print(f"{split:10s} | {s['num_rows']:5d} câu | {s['label_counts']} | "
              f"trung bình {s['avg_words']} từ, dài nhất {s['max_words']} từ")
    print("Ví dụ:", ds["train"][0])

    export_csv(ds)
    out = config.RESULTS_DIR / "dataset_stats.json"
    out.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nĐã xuất CSV vào {config.DATASET_CSV_DIR}")
    print(f"Đã lưu thống kê vào {out}")


if __name__ == "__main__":
    main()
