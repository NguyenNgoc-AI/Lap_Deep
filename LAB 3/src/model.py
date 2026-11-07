"""MODEL — tải model/tokenizer đã huấn luyện sẵn và tóm tắt kiến trúc.

Chạy:  python -m src.model
  In và lưu results/model_summary.txt: kiến trúc, số tham số của
  - model sentiment có sẵn (Exercise 1),
  - DistilBERT gốc gắn lớp phân loại 2 nhãn (Exercise 2, trước fine-tune).
"""
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src import config


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_tokenizer(name=config.BASE_MODEL):
    return AutoTokenizer.from_pretrained(name)


def load_classifier(name=config.BASE_MODEL):
    """DistilBERT + lớp phân loại 2 nhãn. Lớp cuối được khởi tạo mới (sẽ fine-tune)."""
    return AutoModelForSequenceClassification.from_pretrained(
        name,
        num_labels=len(config.ID2LABEL),
        id2label=config.ID2LABEL,
        label2id=config.LABEL2ID,
    )


def load_finetuned(path=config.FINETUNED_DIR):
    if not path.exists():
        raise FileNotFoundError(
            f"Chưa có model fine-tune tại {path}. Hãy chạy trước: python -m src.train")
    return AutoTokenizer.from_pretrained(path), AutoModelForSequenceClassification.from_pretrained(path)


def count_parameters(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def summarize(name, model):
    total, trainable = count_parameters(model)
    head = getattr(model, "classifier", None)
    return "\n".join([
        f"=== {name}",
        f"Kiến trúc: {type(model).__name__}",
        f"Số lớp Transformer: {getattr(model.config, 'n_layers', getattr(model.config, 'num_hidden_layers', '?'))}",
        f"Kích thước ẩn: {getattr(model.config, 'dim', getattr(model.config, 'hidden_size', '?'))}",
        f"Nhãn: {model.config.id2label}",
        f"Tổng tham số: {total:,} | Tham số huấn luyện được: {trainable:,}",
        f"Lớp phân loại cuối: {head}",
        "",
    ])


def main():
    config.ensure_dirs()
    parts = [f"Thiết bị: {get_device()}\n"]
    parts.append(summarize(f"Exercise 1 — {config.SENTIMENT_MODEL}",
                           AutoModelForSequenceClassification.from_pretrained(config.SENTIMENT_MODEL)))
    parts.append(summarize(f"Exercise 2 — {config.BASE_MODEL} (+ lớp phân loại 2 nhãn, chưa fine-tune)",
                           load_classifier()))
    tok = load_tokenizer()
    sample = "I really love this movie, it was amazing!"
    parts.append(f"Tokenizer ví dụ: {sample}\nTokens: {tok.tokenize(sample)}\n"
                 f"Input IDs: {tok(sample)['input_ids']}\n")
    text = "\n".join(parts)
    print(text)
    out = config.RESULTS_DIR / "model_summary.txt"
    out.write_text(text, encoding="utf-8")
    print(f"Đã lưu {out}")


if __name__ == "__main__":
    main()
