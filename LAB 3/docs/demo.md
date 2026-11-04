# Demo

## 0. Luồng demo

```
Người dùng nhập câu tiếng Anh
  → chọn model: Ex1 (có sẵn, --model pretrained) hoặc Ex2 (đã fine-tune, mặc định)
  → tokenizer: truncation, max_length 128, đưa lên GPU nếu có
  → model ở chế độ eval, không tính gradient → 2 logits
  → softmax → nhãn có xác suất cao nhất + độ tin cậy
  → in "NHÃN  xx.xx% | câu"
```

Trình tự gợi ý khi trình bày: (1) chạy `--model pretrained` với câu rõ ràng và câu mỉa mai để thấy giới hạn của model có sẵn; (2) chạy `--compare` để so model Ex1 và Ex2 trên cùng 5 câu; (3) chế độ gõ câu liên tục để người xem tự nhập. Độ tin cậy là đầu ra softmax, chưa được hiệu chuẩn thành xác suất đúng.

## 1. Demo trong notebook

- `notebooks/ex1_sentiment_analysis.ipynb`, hai cell cuối: dự đoán câu mẫu và 4 câu thử bằng model có sẵn.
- `notebooks/ex2_finetuning.ipynb`, bước 7: dùng `pipeline("text-classification", model=trainer.model)` để dự đoán 3 câu tự viết bằng model vừa fine-tune.

Muốn thử câu khác, sửa danh sách câu trong cell rồi chạy lại cell đó.

## 2. Demo bằng script `src/demo.py`

Chạy trong thư mục `LAB 3`, đặt `$py = "D:\Code\.venv\Scripts\python.exe"`:

| Lệnh | Model | Việc làm |
|---|---|---|
| `& $py -m src.demo "This movie was fantastic!"` | Đã fine-tune (Ex2) | Dự đoán một câu |
| `& $py -m src.demo --model pretrained "Not bad at all!"` | Có sẵn (Ex1) | Dự đoán một câu |
| `& $py -m src.demo --compare` | Cả hai | So sánh 2 model trên 5 câu mẫu |
| `& $py -m src.demo --compare "Your sentence"` | Cả hai | So sánh trên câu tự nhập |
| `& $py -m src.demo` | Đã fine-tune | Gõ câu liên tục, `q` để thoát |

Chế độ dùng model đã fine-tune cần chạy `src.train` trước để có `models/distilbert-rotten-tomatoes/`. Chế độ `--model pretrained` dùng được ngay.

5 câu mẫu của `--compare`: "An absolute masterpiece with brilliant acting.", "Boring plot and terrible dialogue.", "Not bad at all!", "The food was okay, nothing special.", "Oh great, another Monday...". Bộ câu này gồm câu tích cực, tiêu cực, phủ định, trung tính và mỉa mai.

Kết quả in ra có dạng:

```
[Exercise 1 — distilbert/distilbert-base-uncased-finetuned-sst-2-english]
  POSITIVE  99.96% | Not bad at all!
  ...
[Exercise 2 — DistilBERT fine-tune trên rotten_tomatoes]
  ...
```

## 3. Kết quả demo đã có

Từ output thật của notebook (chi tiết trong [evaluation.md](evaluation.md)):

| Câu | Model Ex1 | Model Ex2, lần 1 (3 epoch) | Model Ex2, lần 2 (1 epoch) |
|---|---|---|---|
| Not bad at all! | POSITIVE 99.96% | POSITIVE 95.90% | NEGATIVE 66.07% |
| An absolute masterpiece with brilliant acting. | — | POSITIVE 99.67% | POSITIVE 97.78% |
| Boring plot and terrible dialogue. | — | NEGATIVE 99.46% | NEGATIVE 96.69% |

`TODO`: thêm kết quả `src.demo --compare` với model fine-tune mới sau khi chạy `src.train`.

## 4. Kiểm thử script

Toàn bộ chuỗi `src.data → src.model → src.train → src.evaluation → src.demo` (cả 4 chế độ demo) đã chạy không lỗi với một model DistilBERT tí hon và dữ liệu giả lập offline, vì môi trường kiểm thử không truy cập được Hugging Face Hub. Chưa chạy với model và dữ liệu thật — xem [plan-progress.md](plan-progress.md).
