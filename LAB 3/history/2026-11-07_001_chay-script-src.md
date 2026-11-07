# Phiên 2026-11-07_001 · Chạy các script src với dữ liệu thật

- **Người thực hiện:** HuHoww, có Claude hỗ trợ. **WF:** không có. **Trạng thái:** TESTED (`src/` với model và dữ liệu thật).
- **Mục tiêu:** bổ sung dữ liệu train/validation/test (thư mục `data/` trên GitHub đang trống) và kết quả của các script `src`, thay các chỗ `TODO` trong tài liệu.

## Chạy (GPU RTX 3050 6GB, `D:\Code\Lap_Deep\LAB 3`)

| Lệnh | Kết quả |
|---|---|
| `python -m src.data` | `data/rotten_tomatoes/train.csv` (8.530), `validation.csv` (1.066), `test.csv` (1.066); mỗi tập cân bằng neg/pos; số từ trung bình 21.0–21.2, dài nhất 59 |
| `python -m src.model` | `results/model_summary.txt`; 66.955.010 tham số; lần đầu tải model Ex1 theo tên `distilbert/...` (~268 MB) |
| `python -m src.train` | 3 epoch, 1.602 bước, 131,5 giây; validation loss 0.3450 / 0.4067 / 0.4874, accuracy 83.58% / 84.62% / 84.52% (giống hệt notebook); chọn epoch 2 |
| `python -m src.evaluation` | Model epoch 2 trên test: accuracy 84.62%, precision 85.69%, recall 83.11%, F1 84.38%; chưa fine-tune 42.87% / F1 14.10%; confusion matrix [[459, 74], [90, 443]]; 164 câu sai |
| `python -m src.demo --compare` | Ex1 tự tin 98–99.99% ở cả 5 câu, sai câu mỉa mai; Ex2 đoán câu mỉa mai NEGATIVE 51.22% |

## Lỗi và sửa

| File | Lỗi | Sửa |
|---|---|---|
| `src/model.py` | In `Kiến trúc: ['DistilBertForMaskedLM']` cho Ex2 (lấy từ config gốc trên Hub) dù model nạp là `DistilBertForSequenceClassification` | In `type(model).__name__`; chạy lại `src.model` |
| `src/evaluation.py` | Treo khi tính chỉ số: mỗi lần gọi `evaluate.load` đều hỏi Hugging Face Hub; `precision` không có bản lưu nên lần đầu chuyển sang sklearn, lần sau đứng chờ mạng | Nạp `evaluate` (accuracy, F1) một lần với `HF_EVALUATE_OFFLINE=1`; precision, recall bằng sklearn; công thức không đổi |

Hai sửa đổi không làm thay đổi kết quả notebook hay số liệu đã báo cáo.

## File cập nhật

`docs/evaluation.md`, `docs/training.md`, `docs/demo.md`, `docs/data.md`, `docs/model.md`, `docs/plan-progress.md`, `PROJECT_STATE.md`, `README.md`, `AI_USAGE.md`, `src/model.py`, `src/evaluation.py`, file log này. Mới trong repo: `data/rotten_tomatoes/*.csv`, `results/*`.

## Việc tiếp theo (chưa thực hiện)

- Commit và push lên nhánh `Lab3` (không gồm `models/`, khoảng 1,9 GB gồm model và checkpoint).
- Thành viên khác bổ sung `AI_USAGE.md`; điền họ tên, MSSV trong báo cáo.
