# Lab 3 — Practice 3: Get started with Hugging Face

Dùng thư viện Hugging Face (`transformers`, `datasets`, `evaluate`) để:

- **Exercise 1:** phân tích cảm xúc một câu bằng model có sẵn `distilbert-base-uncased-finetuned-sst-2-english`.
- **Exercise 2:** fine-tune `distilbert/distilbert-base-uncased` cho phân loại cảm xúc 2 lớp trên bộ review phim `rotten_tomatoes`.

Kết quả đã có: Exercise 1 đúng với câu có cảm xúc rõ và câu phủ định, sai với câu mỉa mai. Exercise 2 (3 epoch trên GPU RTX 3050, 2 phút) đạt **test accuracy 84.62%, F1 84.67%**, từ 45.22% trước fine-tune; validation loss tăng từ epoch 2 cho thấy overfitting. Chi tiết: [docs/evaluation.md](docs/evaluation.md). Còn lại: chạy các script `src/` với dữ liệu thật — xem [docs/plan-progress.md](docs/plan-progress.md).

## Tài liệu

Tổ chức theo `RULES.md` v1.1 của nhóm (§11, §12, §19).


| File | Nội dung |
|---|---|
| [docs/labs3-description.md](docs/labs3-description.md) | Đề bài, 5W1H, input/output, luồng xử lý, bảng đối chiếu từng yêu cầu |
| [docs/data.md](docs/data.md) | Bộ dữ liệu rotten_tomatoes, phân chia train/validation/test, tiền xử lý |
| [docs/model.md](docs/model.md) | Các model, kiến trúc DistilBERT, lớp phân loại mới, lưu/nạp model |
| [docs/training.md](docs/training.md) | Tham số huấn luyện, notebook và script, các lần chạy, overfitting |
| [docs/evaluation.md](docs/evaluation.md) | Chỉ số, kết quả Exercise 1 và 2, nhận xét |
| [docs/demo.md](docs/demo.md) | Cách chạy demo và kết quả dự đoán |
| [docs/plan-progress.md](docs/plan-progress.md) | Kế hoạch, mốc tiến độ, đã hoàn thành, đang làm, còn thiếu |
| [PROJECT_STATE.md](PROJECT_STATE.md) | Trạng thái từng phase, thay đổi quan trọng, blocker |
| [history/](history/) | Nhật ký từng phiên làm việc |
| [AI_USAGE.md](AI_USAGE.md) | Khai báo việc sử dụng AI |

## Cấu trúc thư mục

```text
LAB 3/
├── README.md
├── AI_USAGE.md
├── PROJECT_STATE.md
├── requirements.txt
├── docs/                          ← 7 file theo RULES.md v1.1 §19 (bảng trên)
├── history/                       ← nhật ký từng phiên (RULES §11)
├── notebooks/
│   ├── ex1_sentiment_analysis.ipynb   ← Exercise 1
│   └── ex2_finetuning.ipynb           ← Exercise 2, theo đúng 7 bước của đề
├── src/                           ← Exercise 2 tách thành các bước chạy bằng lệnh
│   ├── config.py                  ← tên model, dataset, siêu tham số, đường dẫn
│   ├── data.py                    ← tải, thống kê, xuất CSV, tokenize
│   ├── model.py                   ← tải model/tokenizer, tóm tắt kiến trúc
│   ├── train.py                   ← fine-tune bằng Trainer
│   ├── evaluation.py              ← đánh giá trên tập test
│   └── demo.py                    ← dự đoán câu bất kỳ
├── data/                          ← CSV do src.data tạo
├── models/                        ← model sau fine-tune (không đưa lên GitHub)
└── results/                       ← số liệu và biểu đồ do các script tạo
```

## Cài đặt

Dùng `.venv` tại `D:\Code`. Máy có GPU NVIDIA cài PyTorch bản CUDA trước:

```powershell
D:\Code\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cu126
D:\Code\.venv\Scripts\python.exe -m pip install -r requirements.txt
D:\Code\.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Lần chạy đầu cần mạng để tải model (~250 MB) và dữ liệu.

## Cách chạy

**Notebook:** mở file trong `notebooks/` bằng VS Code, chọn kernel `.venv`, **Restart Kernel → Run All**.

**Script** — mở terminal trong thư mục `LAB 3`:

```powershell
cd "D:\Code\DL\LAB 3"
$py = "D:\Code\.venv\Scripts\python.exe"

& $py -m src.data            # Data
& $py -m src.model           # Model
& $py -m src.train           # Training (~2 phút trên RTX 3050)
& $py -m src.evaluation      # Evaluation trên tập test
& $py -m src.demo --compare  # Demo: so sánh model Ex1 và Ex2
```

Máy chỉ có CPU: chạy `$env:LAB3_TRAIN_LIMIT = "2000"` trước `src.train`.

## Lưu ý khi đưa lên GitHub

- Bài nằm ở nhánh **`Lab3`**.
- Không đưa `models/distilbert-rotten-tomatoes/` và `models/checkpoints/` lên (~255 MB, vượt giới hạn 100 MB/file); `.gitignore` đã loại trừ. Khi upload qua web GitHub, tự bỏ các thư mục này.
