# Model

## 1. Các model dùng trong bài

| Model | Bài | Vai trò | Nơi lấy |
|---|---|---|---|
| `distilbert-base-uncased-finetuned-sst-2-english` | Exercise 1 | Model sentiment có sẵn, dùng trực tiếp | Hugging Face Hub (tự tải) |
| `distilbert/distilbert-base-uncased` | Exercise 2 | Model gốc để fine-tune | Hugging Face Hub (tự tải) |
| `models/distilbert-rotten-tomatoes/` | Exercise 2 | Model sau fine-tune | Tạo bởi `python -m src.train` |

## 2. Lý do chọn model

| Model | Lý do |
|---|---|
| `distilbert-base-uncased-finetuned-sst-2-english` (Ex1) | Model sentiment tiếng Anh phổ biến trên Hub, là mặc định của `pipeline("sentiment-analysis")`, đã fine-tune trên SST-2 (review phim) nên dùng ngay được, cùng miền với dữ liệu Ex2 |
| `distilbert/distilbert-base-uncased` (Ex2) | Nhỏ hơn BERT-base khoảng 40% (khoảng 66 triệu so với 110 triệu tham số) và nhanh hơn, vừa GPU laptop 6 GB với batch 16 và fp16; cùng họ với model Ex1 nên dễ so sánh kết quả hai bài |
| Bản `uncased` | Dữ liệu rotten_tomatoes đã viết thường, nên tokenizer không phân biệt hoa/thường là phù hợp |

## 3. Kiến trúc DistilBERT

DistilBERT là bản rút gọn của BERT (khoảng 66 triệu tham số), giữ phần lớn khả năng hiểu ngôn ngữ nhưng nhỏ và nhanh hơn, phù hợp GPU laptop 6 GB.

```
Câu → Tokenizer (WordPiece, uncased) → input_ids
    → Embedding (768 chiều) → 6 lớp Transformer encoder
    → vector của token [CLS]
    → pre_classifier: Linear(768, 768) + ReLU + Dropout
    → classifier: Linear(768, 2) → logits [NEGATIVE, POSITIVE]
    → softmax → xác suất, argmax → nhãn
```

`AutoModelForSequenceClassification` tự gắn hai lớp `pre_classifier` và `classifier` phía trên phần DistilBERT gốc.

## 4. Exercise 1 — model có sẵn

- Đã được fine-tune trên SST-2 (câu review phim, 2 nhãn) nên dùng được ngay, không cần huấn luyện.
- Nhãn: `{0: 'NEGATIVE', 1: 'POSITIVE'}`.
- Tokenize câu mẫu "I really love this movie, it was amazing!":
  - Tokens: `['i', 'really', 'love', 'this', 'movie', ',', 'it', 'was', 'amazing', '!']`
  - Input IDs: `[101, 1045, 2428, 2293, 2023, 3185, 1010, 2009, 2001, 6429, 999, 102]` — 101 = `[CLS]`, 102 = `[SEP]`.

## 5. Exercise 2 — model trước fine-tune

Tải bằng:

```python
AutoModelForSequenceClassification.from_pretrained(
    "distilbert/distilbert-base-uncased",
    num_labels=2,
    id2label={0: "NEGATIVE", 1: "POSITIVE"},
    label2id={"NEGATIVE": 0, "POSITIVE": 1},
)
```

Khi tải, thư viện in bảng báo cáo trọng số:

| Trạng thái | Lớp | Ý nghĩa |
|---|---|---|
| MISSING | `pre_classifier.weight/bias`, `classifier.weight/bias` | Không có trong model gốc → khởi tạo ngẫu nhiên; đây là phần fine-tune phải học |
| UNEXPECTED | `vocab_transform`, `vocab_layer_norm`, `vocab_projector` | Phần dự đoán từ bị che (masked LM) lúc pre-train; không dùng cho phân loại nên bỏ qua |

Đây là cảnh báo bình thường, không phải lỗi. Vì lớp phân loại còn ngẫu nhiên, accuracy trước fine-tune chỉ khoảng 42–45% (xem [evaluation.md](evaluation.md)).

Fine-tune cập nhật **toàn bộ** tham số (không đóng băng lớp nào). Siêu tham số quan trọng (learning rate 2e-5, batch 16, 3 epoch, max length 128): xem [training.md](training.md).

## 6. Lưu và nạp model

- `src/train.py` lưu model tốt nhất (theo validation accuracy) và tokenizer vào `models/distilbert-rotten-tomatoes/` bằng `trainer.save_model()` và `tokenizer.save_pretrained()`.
- `src/evaluation.py` và `src/demo.py` nạp lại bằng `AutoModelForSequenceClassification.from_pretrained("models/distilbert-rotten-tomatoes")`.
- Notebook `ex2_finetuning.ipynb` không lưu model ra đĩa (`save_strategy="no"`).
- Model sau fine-tune nặng khoảng 255 MB, vượt giới hạn 100 MB/file của GitHub, nên **không đưa lên repo** (`.gitignore`). Mỗi thành viên tạo lại bằng `src.train` (khoảng 2 phút trên RTX 3050).

`python -m src.model` in và lưu `results/model_summary.txt`: kiến trúc, số lớp, kích thước ẩn, tổng tham số và tham số huấn luyện được của cả hai model, kèm ví dụ tokenize.
