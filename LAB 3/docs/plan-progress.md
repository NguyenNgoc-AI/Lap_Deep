# Plan — Progress: Lab 3

- Cập nhật: 2026-11-04, Asia/Ho_Chi_Minh.
- Repo: `NguyenNgoc-AI/Lap_Deep`, nhánh **`Lab3`**, thư mục `LAB 3/`. Nhánh `main` đã xóa `LAB 3` ngày 2026-11-01 (commit `4f1f92f`).
- Trạng thái chung: **IN PROGRESS** — code, notebook và tài liệu đủ; còn chạy lại Exercise 2 và điền kết quả cuối (`PENDING_UPDATE`).
- Tài liệu theo `RULES.md` v1.1 §19 của nhóm (bản trong `Lab2/` trên nhánh `lab2.1`). Trạng thái tổng hợp: [`../PROJECT_STATE.md`](../PROJECT_STATE.md). Nhật ký từng phiên: [`../history/`](../history/).

## 1. Kế hoạch thực hiện

| Bước | Nội dung | Sản phẩm |
|---|---|---|
| P01 · Description | Phân tích đề, xác định bài toán, input/output | `docs/labs3-description.md` |
| P02 · Exercise 1 | Model sentiment có sẵn, tokenize, phân tích cảm xúc | `notebooks/ex1_sentiment_analysis.ipynb` |
| P03 · Data | Tải rotten_tomatoes, mô tả, tiền xử lý | `src/data.py`, `docs/data.md` |
| P04 · Model | Tải DistilBERT, lớp phân loại 2 nhãn | `src/model.py`, `docs/model.md` |
| P05 · Training | `TrainingArguments`, `Trainer`, theo dõi validation | `notebooks/ex2_finetuning.ipynb`, `src/train.py`, `docs/training.md` |
| P06 · Evaluation | Đánh giá test bằng `evaluate`, confusion matrix | `src/evaluation.py`, `docs/evaluation.md` |
| P07 · Demo | Dự đoán câu bất kỳ, so sánh model Ex1/Ex2 | `src/demo.py`, `docs/demo.md` |
| P08 · Bàn giao | README, AI_USAGE, báo cáo, upload GitHub | `README.md`, `AI_USAGE.md`, báo cáo, nhánh `Lab3` |

## 2. Mốc tiến độ

| Ngày | Người | Mốc |
|---|---|---|
| 2026-10-27 | HuHoww | Nhận đề, phân tích yêu cầu 2 bài |
| 2026-10-28 | HuHoww (HUYNH HUU HAO) | Ex1 xong; Ex2 bản đầu chạy đủ 3 epoch trên GPU (84.62% trên test); commit "Thêm Lab 3" |
| 2026-10-30 | HoangKhanh1904 | "Sửa ex2": tách validation/test, đánh giá test riêng, viết lại nhận xét; chạy được 1 epoch trên CPU |
| 2026-11-01 | HuHoww | Xóa `LAB 3` khỏi `main`; thêm `src/`, `docs/`, `AI_USAGE.md`, báo cáo; sắp xếp notebook vào `notebooks/` |
| 2026-11-04 | HuHoww | Rà soát theo `RULES.md` v1.1: đổi tên file docs, thêm 5W1H, schema, lý do chọn model, luồng demo, `PROJECT_STATE.md`, `history/` |

## 3. Đã hoàn thành

| Hạng mục | Bằng chứng |
|---|---|
| P01 Description | `docs/labs3-description.md`: đề, 5W1H, input/output, luồng xử lý, bảng đối chiếu 11 yêu cầu |
| P02 Exercise 1 | Output notebook: tokenize câu mẫu, POSITIVE 99.99%, 4 câu thử, nhận xét |
| Ex2 lần 1 (bản đầu) | 3 epoch, GPU, 118,6 giây; test 84.62%, F1 84.67%; bằng chứng overfitting (loss đánh giá 0.3625 → 0.5470) |
| Code `src/` (P03–P07) | `py_compile` PASS; chuỗi `data → model → train → evaluation → demo` chạy không lỗi với **model tí hon và dữ liệu giả lập offline** |
| Tài liệu `docs/` (7 file) | Mọi con số đối chiếu với output notebook |

## 4. Đang làm

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Ex2 notebook bản hiện tại | **NEEDS RERUN** | Code đặt 3 epoch nhưng output chỉ có 1 epoch trên CPU; cell `TrainingArguments` chưa chạy lại sau khi sửa |
| `AI_USAGE.md` | IN PROGRESS | Phần của HuHoww đã điền; thành viên khác tự bổ sung mục 8 |
| Báo cáo (tài liệu Claude Docs, xuất Word/PDF) | IN PROGRESS | Mục 6.4 kết quả cuối, họ tên và MSSV thành viên còn trống |

## 5. Còn thiếu

| # | Việc | Trạng thái |
|---|---|---|
| 1 | Restart & Run All `notebooks/ex2_finetuning.ipynb` trên GPU, lưu lại | TODO |
| 2 | Chạy `src.data`, `src.model`, `src.train`, `src.evaluation`, `src.demo --compare` với model và dữ liệu thật → tạo `data/rotten_tomatoes/*.csv`, `results/*` | TODO |
| 3 | Điền bảng "Kết quả cuối" trong `docs/evaluation.md`, `docs/training.md` (lần 3), `docs/demo.md`, README, báo cáo | `PENDING_UPDATE` |
| 4 | Thành viên khác khai báo trong `AI_USAGE.md` | TODO |
| 5 | Ghi nhật ký phiên chạy lại vào `history/`, cập nhật `PROJECT_STATE.md` và file này | TODO |
| 6 | Upload `LAB 3/` lên nhánh `Lab3` (không kèm `models/distilbert-rotten-tomatoes/`, `models/checkpoints/`) | TODO |

## 6. Môi trường

- Máy GPU: laptop Windows, NVIDIA GeForce RTX 3050 6GB Laptop GPU; Python trong `D:\Code\.venv`; `torch 2.14.1+cu126`, `transformers 5.21.0`.
- Lần 2 chạy trên một máy khác, chỉ có CPU.
- Lưu ý API: Hugging Face Hub bản mới yêu cầu tên dạng `tổ_chức/tên`; Transformers 5 dùng `eval_strategy` và `processing_class`.
