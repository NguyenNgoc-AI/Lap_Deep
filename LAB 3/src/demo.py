"""DEMO — dự đoán cảm xúc cho câu tiếng Anh bất kỳ.

Chạy:
  python -m src.demo "This movie was fantastic!"         # model đã fine-tune (Exercise 2)
  python -m src.demo --model pretrained "Not bad at all!"  # model có sẵn (Exercise 1)
  python -m src.demo --compare                           # so sánh 2 model trên các câu mẫu
  python -m src.demo                                     # chế độ gõ câu liên tục, gõ q để thoát
"""
import argparse

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src import config

EXAMPLES = [
    "An absolute masterpiece with brilliant acting.",
    "Boring plot and terrible dialogue.",
    "Not bad at all!",
    "The food was okay, nothing special.",
    "Oh great, another Monday...",
]


class SentimentModel:
    def __init__(self, which="finetuned"):
        if which == "pretrained":
            path, self.name = config.SENTIMENT_MODEL, f"Exercise 1 — {config.SENTIMENT_MODEL}"
        else:
            path = config.FINETUNED_DIR
            if not path.exists():
                raise SystemExit("Chưa có model fine-tune. Hãy chạy: python -m src.train "
                                 "(hoặc dùng --model pretrained).")
            path, self.name = str(path), "Exercise 2 — DistilBERT fine-tune trên rotten_tomatoes"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForSequenceClassification.from_pretrained(path).to(self.device).eval()

    @torch.no_grad()
    def predict(self, sentences):
        batch = self.tokenizer(sentences, padding=True, truncation=True,
                               max_length=config.MAX_LENGTH, return_tensors="pt").to(self.device)
        probs = torch.softmax(self.model(**batch).logits, dim=-1).cpu()
        labels = self.model.config.id2label
        return [(labels[int(p.argmax())], float(p.max())) for p in probs]


def show(model, sentences):
    print(f"\n[{model.name}]")
    for s, (label, conf) in zip(sentences, model.predict(sentences)):
        print(f"  {label:8s} {conf:7.2%} | {s}")


def main():
    parser = argparse.ArgumentParser(description="Demo phân tích cảm xúc (Lab 3)")
    parser.add_argument("text", nargs="*", help="Câu cần dự đoán")
    parser.add_argument("--model", choices=["finetuned", "pretrained"], default="finetuned")
    parser.add_argument("--compare", action="store_true", help="So sánh 2 model trên các câu mẫu")
    args = parser.parse_args()

    if args.compare:
        sentences = [" ".join(args.text)] if args.text else EXAMPLES
        for which in ("pretrained", "finetuned"):
            show(SentimentModel(which), sentences)
        return

    model = SentimentModel(args.model)
    if args.text:
        show(model, [" ".join(args.text)])
        return

    print(f"Model: {model.name} | thiết bị: {model.device}")
    print("Gõ một câu tiếng Anh rồi Enter (gõ q để thoát).")
    while True:
        try:
            s = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if s.lower() in {"q", "quit", "exit"}:
            break
        if s:
            label, conf = model.predict([s])[0]
            print(f"  {label} ({conf:.2%})")


if __name__ == "__main__":
    main()
