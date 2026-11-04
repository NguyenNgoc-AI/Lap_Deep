# Evaluation — Đánh giá kết quả

## 1. Chỉ số dùng

| Chỉ số | Ý nghĩa |
|---|---|
| Accuracy | Tỉ lệ câu dự đoán đúng |
| Precision (lớp POSITIVE) | Trong các câu model đoán POSITIVE, bao nhiêu câu đúng |
| Recall (lớp POSITIVE) | Trong các câu thật sự POSITIVE, model tìm ra bao nhiêu |
| F1 | Trung bình điều hòa của precision và recall |
| Confusion matrix | Hàng = nhãn thật, cột = nhãn dự đoán |
| Loss | Cross-entropy trên tập đánh giá; phản ánh cả độ tự tin của dự đoán |

Accuracy và F1 tính bằng thư viện `evaluate` (`evaluate.load("accuracy")`, `evaluate.load("f1")`). `src/evaluation.py` tính thêm precision, recall, báo cáo theo lớp và confusion matrix.

## 2. Exercise 1 — model có sẵn

| Câu | Dự đoán | Độ tin cậy | Đánh giá |
|---|---|---|---|
| I really love this movie, it was amazing! | POSITIVE | 99.99% | Đúng |
| This product is terrible, I want my money back. | NEGATIVE | 99.98% | Đúng |
| The food was okay, nothing special. | NEGATIVE | 98.34% | Câu trung tính, model chỉ có 2 nhãn nên buộc chọn một bên |
| Not bad at all! | POSITIVE | 99.96% | Đúng, hiểu phủ định "not bad" |
| Oh great, another Monday... | POSITIVE | 99.70% | Sai, không nhận ra mỉa mai |

Model đúng với câu có cảm xúc rõ và câu phủ định, nhưng sai với câu mỉa mai và vẫn tự tin trên 98% với cả câu trung tính lẫn câu đoán sai: độ tin cậy cao không đồng nghĩa với đúng.

## 3. Exercise 2 — kết quả fine-tune

### Lần 1 — bản đầu, 3 epoch, GPU (đánh giá trên tập test sau mỗi epoch)

| Thời điểm | Loss | Accuracy | F1 |
|---|---|---|---|
| Trước fine-tune | 0.6973 | 42.87% | 14.10% |
| Sau epoch 1 | 0.3625 | 84.43% | 84.01% |
| Sau epoch 2 | 0.4408 | 84.62% | 84.38% |
| Sau epoch 3 | 0.5470 | **84.62%** | **84.67%** |

### Lần 2 — bản tách validation/test, dừng sau 1 epoch, CPU

| Tập | Thời điểm | Loss | Accuracy | F1 |
|---|---|---|---|---|
| Validation | Trước fine-tune | 0.6968 | 45.12% | 17.49% |
| Validation | Sau epoch 1 | 0.3569 | 83.96% | 84.00% |
| Test | Sau epoch 1 | 0.3834 | **83.58%** | **83.72%** |

### Câu tự viết

| Câu | Lần 1 (3 epoch) | Lần 2 (1 epoch) |
|---|---|---|
| An absolute masterpiece with brilliant acting. | POSITIVE 99.67% | POSITIVE 97.78% |
| Boring plot and terrible dialogue. | NEGATIVE 99.46% | NEGATIVE 96.69% |
| Not bad at all! | POSITIVE 95.90% | NEGATIVE 66.07% (sai) |

### Kết quả cuối — `PENDING_UPDATE` (chờ chạy lại)

| Nguồn | Validation trước | Validation sau | Test accuracy | Test F1 |
|---|---|---|---|---|
| Notebook, cuối epoch 3 | Chờ chạy lại | Chờ chạy lại | Chờ chạy lại | Chờ chạy lại |
| `src.train` + `src.evaluation`, epoch tốt nhất | Chờ chạy | Chờ chạy | Chờ chạy | Chờ chạy |

Sau khi chạy `src.evaluation`, các file trong `results/` bổ sung: `test_metrics.json` (chỉ số trước/sau, theo lớp, confusion matrix), `confusion_matrix.png`, `misclassified.csv` (các câu đoán sai kèm độ tin cậy).

## 4. Nhận xét

- **Tác dụng của fine-tune:** trước fine-tune lớp phân loại là trọng số ngẫu nhiên, model gần như chỉ đoán một nhãn (accuracy 42–45%, F1 14–17%). Chỉ 1 epoch đã lên khoảng 84%, nhờ tri thức ngôn ngữ DistilBERT học sẵn.
- **Overfitting:** ở lần 1, loss đánh giá tăng từ 0.3625 lên 0.5470 trong khi accuracy chỉ tăng từ 84.43% lên 84.62%. Accuracy gần như không đổi nhưng loss tăng nghĩa là model đoán sai với độ tự tin cao hơn. Với bộ dữ liệu này 1–2 epoch là đủ.
- **Câu phủ định:** sau 1 epoch model còn đoán sai "Not bad at all!"; sau 3 epoch đã đúng. Câu phủ định cần model hiểu ngữ cảnh hơn là từ khóa đơn lẻ.
- **Quy trình:** bản đầu theo dõi bằng tập test nên con số test không còn khách quan; bản sửa dùng validation để theo dõi và test chỉ một lần, đúng quy trình hơn. Hai lần chạy khác tập đánh giá và khác số epoch nên không so sánh trực tiếp từng con số.
