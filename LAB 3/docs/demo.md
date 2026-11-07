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

Chế độ dùng model đã fine-tune cần chạy `src.train` trước để có `models/distilbert-rotten-tomatoes/` (model không có trên GitHub, mỗi máy tự tạo). Chế độ `--model pretrained` dùng được ngay.

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

Kết quả `src.demo --compare` (07/11, model Ex2 = epoch 2 do `src.train` lưu):

| Câu | Model Ex1 (có sẵn, SST-2) | Model Ex2 (fine-tune rotten_tomatoes) |
|---|---|---|
| An absolute masterpiece with brilliant acting. | POSITIVE 99.99% | POSITIVE 99.40% |
| Boring plot and terrible dialogue. | NEGATIVE 99.98% | NEGATIVE 99.18% |
| Not bad at all! | POSITIVE 99.96% | POSITIVE 89.50% |
| The food was okay, nothing special. | NEGATIVE 98.34% | NEGATIVE 90.04% |
| Oh great, another Monday... | POSITIVE 99.70% (sai) | NEGATIVE 51.22% |

- Hai model đồng ý ở 4/5 câu. Model Ex1 luôn tự tin trên 98%, kể cả câu trung tính và câu mỉa mai bị đoán sai.
- Model Ex2 đoán câu mỉa mai là NEGATIVE nhưng chỉ 51.22%, gần như đoán may; với câu phủ định và câu trung tính, độ tin cậy cũng thấp hơn (89–90%). Model Ex2 "biết mình không chắc" hơn ở các câu khó, nhưng chưa đủ để nói nó hiểu mỉa mai.

## 4. Kiểm thử script

- Chạy với model và dữ liệu thật trên GPU (07/11): `src.data`, `src.model`, `src.train`, `src.evaluation`, `src.demo --compare` đều chạy xong, kết quả ở `results/` và bảng trên.
- Trước đó (01/11), toàn bộ chuỗi đã được thử với model DistilBERT tí hon và dữ liệu giả lập offline.
