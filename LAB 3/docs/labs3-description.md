# Lab 3 — Mô tả bài: Practice 3, Get started with Hugging Face

## 1. Đề bài

**Exercise 1: Sentiment Analysis with Hugging Face**

1. Install the Hugging Face `transformers` library.
2. Use a pre-trained sentiment analysis model from the Hugging Face Hub.
3. Tokenize a sample sentence.
4. Perform sentiment analysis on the sentence.

**Exercise 2: Finetuning a Pretrained Model for Binary Text Classification**

1. Install the necessary Hugging Face libraries (`transformers`, `datasets`, `evaluate`).
2. Load a simple dataset for binary text classification.
3. Load a pretrained model and its tokenizer.
4. Preprocess the dataset to be suitable for the model.
5. Define training arguments.
6. Create a `Trainer` object and finetune the model.
7. Evaluate the finetuned model.

Tài liệu tham khảo của đề: xem mục 7.

## 2. Mô tả bằng 5W1H

| Câu hỏi | Trả lời |
|---|---|
| **What — Làm gì?** | Ex1: dùng model sentiment có sẵn để tokenize và phân loại cảm xúc câu tiếng Anh. Ex2: fine-tune DistilBERT cho phân loại cảm xúc 2 lớp trên rotten_tomatoes, đánh giá accuracy/F1, demo dự đoán câu mới. |
| **Why — Vì sao?** | Làm quen hệ sinh thái Hugging Face (Hub, `transformers`, `datasets`, `evaluate`, `Trainer`) và thấy tác dụng của fine-tune: model chưa học (lớp phân loại ngẫu nhiên) so với model sau fine-tune trên cùng dữ liệu. |
| **Who — Ai tham gia?** | Nhóm sinh viên viết code, chạy, giải thích kết quả (phân công ở [plan-progress.md](plan-progress.md) và `AI_USAGE.md`). Giảng viên đối chiếu tài liệu với notebook, code và kết quả. Người dùng demo nhập câu cần phân loại. |
| **When — Khi nào?** | 27/10 nhận đề; 28/10 làm Ex1, Ex2 bản đầu; 30/10 sửa Ex2 (tách validation/test); 01–04/11 bổ sung `src/`, `docs/` và tài liệu. Theo dõi validation sau mỗi epoch; chỉ đánh giá test sau khi train xong. |
| **Where — Ở đâu?** | Chạy local trên laptop Windows, GPU RTX 3050 6GB, Python trong `D:\Code\.venv`, VS Code + Jupyter. Model và dữ liệu tải từ Hugging Face Hub. Bài nộp ở nhánh `Lab3` của repo `NguyenNgoc-AI/Lap_Deep`. |
| **How — Làm thế nào?** | Ex1: tokenizer → model → softmax. Ex2: tải dữ liệu → tokenize → gắn lớp phân loại 2 nhãn → `TrainingArguments` + `Trainer` → đánh giá bằng `evaluate`. Notebook theo đúng 7 bước; `src/` tách cùng quy trình thành từng file chạy bằng lệnh. |

## 3. Input, output và kiến trúc tổng quát

| Hoạt động | Input | Output |
|---|---|---|
| Ex1 — phân tích cảm xúc | Một câu tiếng Anh | Token, input IDs, nhãn `POSITIVE`/`NEGATIVE` + độ tin cậy |
| Ex2 — huấn luyện | 8.530 câu train có nhãn, 1.066 câu validation, model `distilbert-base-uncased`, `TrainingArguments` | Model đã fine-tune, loss/accuracy/F1 validation theo epoch, log và biểu đồ loss |
| Ex2 — đánh giá | Model đã chọn, 1.066 câu test có nhãn | Accuracy, precision, recall, F1, confusion matrix, danh sách câu đoán sai |
| Demo | Một câu tiếng Anh bất kỳ, model Ex1 hoặc Ex2 | Nhãn dự đoán và độ tin cậy |

Luồng xử lý chung:

```
Câu tiếng Anh
  → Tokenizer (WordPiece, uncased; [CLS] … [SEP]; cắt 128 token)
  → DistilBERT (6 lớp Transformer)
  → vector [CLS] → lớp phân loại → 2 logits
  → softmax → xác suất 2 lớp → argmax → NEGATIVE / POSITIVE

Ex2 thêm vòng huấn luyện:
  rotten_tomatoes (train) → Trainer: forward → cross-entropy → backward → AdamW
  → đánh giá validation mỗi epoch → model cuối / epoch tốt nhất → đánh giá test một lần
```

Chi tiết: [data.md](data.md) · [model.md](model.md) · [training.md](training.md) · [evaluation.md](evaluation.md) · [demo.md](demo.md).

## 4. Bài toán

| | Exercise 1 | Exercise 2 |
|---|---|---|
| Loại bài | Suy luận (inference) với model có sẵn | Fine-tune model đã huấn luyện sẵn |
| Đầu vào | Một câu tiếng Anh | Câu review phim tiếng Anh |
| Đầu ra | `POSITIVE` / `NEGATIVE` + độ tin cậy | `POSITIVE` / `NEGATIVE` (0 = neg, 1 = pos) |
| Model | `distilbert-base-uncased-finetuned-sst-2-english` | `distilbert/distilbert-base-uncased` + lớp phân loại 2 nhãn |
| Dữ liệu | Câu tự viết | `cornell-movie-review-data/rotten_tomatoes` |
| Chỉ số | Độ tin cậy (softmax) | Accuracy, F1 (thêm precision, recall, confusion matrix trong script) |

Model dự đoán bằng cách đưa câu qua tokenizer → model → logits 2 giá trị → softmax → chọn nhãn có xác suất lớn nhất (`argmax`).

## 5. Đối chiếu yêu cầu và nơi thực hiện

| Yêu cầu | Cách thực hiện | Notebook | Script | Tài liệu |
|---|---|---|---|---|
| Ex1.1 Cài `transformers` | Cài vào `.venv`, in phiên bản, kiểm tra GPU | `notebooks/ex1_sentiment_analysis.ipynb` cell 1 | `requirements.txt` | README |
| Ex1.2 Model sentiment có sẵn | `AutoModelForSequenceClassification` từ Hub | cell 2 | `src/model.py` | [model.md](model.md) |
| Ex1.3 Tokenize câu mẫu | In token và input IDs | cell 3 | `src/model.py` | [model.md](model.md) |
| Ex1.4 Phân tích cảm xúc | Softmax trên logits | cell 4–5 | `src/demo.py --model pretrained` | [demo.md](demo.md), [evaluation.md](evaluation.md) |
| Ex2.1 Cài thư viện | `transformers`, `datasets`, `evaluate`, `accelerate` | `notebooks/ex2_finetuning.ipynb` bước 1 | `requirements.txt` | README |
| Ex2.2 Tải dữ liệu 2 lớp | `load_dataset("cornell-movie-review-data/rotten_tomatoes")` | bước 2 | `src/data.py` | [data.md](data.md) |
| Ex2.3 Model và tokenizer | `distilbert/distilbert-base-uncased`, `num_labels=2` | bước 3 | `src/model.py` | [model.md](model.md) |
| Ex2.4 Tiền xử lý | Tokenize, `truncation`, `max_length=128`, padding động | bước 4 | `src/data.py` | [data.md](data.md) |
| Ex2.5 Training arguments | `TrainingArguments` | bước 5 | `src/train.py` | [training.md](training.md) |
| Ex2.6 Trainer, fine-tune | `Trainer(...).train()`, theo dõi validation | bước 6 | `src/train.py` | [training.md](training.md) |
| Ex2.7 Đánh giá | Thư viện `evaluate` trên tập test | bước 7 | `src/evaluation.py` | [evaluation.md](evaluation.md) |

## 6. Phạm vi và giới hạn

- Chỉ dùng DistilBERT (một kiến trúc), một bộ dữ liệu, một seed (42); không so sánh nhiều cấu hình siêu tham số.
- Model có 2 nhãn nên không biểu diễn được câu trung tính.
- Notebook là bản theo đúng 7 bước của đề; `src/` là cùng quy trình tách thành file để chạy bằng lệnh và lưu kết quả vào `results/`.

## 7. Tài liệu tham khảo (theo đề)

- [Hugging Face — Fine-tune a pretrained model](https://huggingface.co/docs/transformers/en/training#fine-tune-a-pretrained-model)
- [Hugging Face — Getting Started with Sentiment Analysis using Python](https://huggingface.co/blog/sentiment-analysis-python)
- [Kaggle — Sentiment analysis using Hugging Face](https://www.kaggle.com/code/gauravduttakiit/sentiment-analysis-using-hugging-face)
- [Kaggle — Fine-tuning BERT for text classification](https://www.kaggle.com/code/neerajmohan/fine-tuning-bert-for-text-classification)
