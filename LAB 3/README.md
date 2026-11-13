# Lab 3 — Practice 3: Get started with Hugging Face

## Tổng quan dự án

| | |
|---|---|
| **Mục tiêu** | Làm quen hệ sinh thái Hugging Face (Hub, `transformers`, `datasets`, `evaluate`, `Trainer`) và thấy tác dụng của fine-tune một model ngôn ngữ đã huấn luyện sẵn. |
| **Bài toán** | Phân loại cảm xúc câu review phim tiếng Anh thành `NEGATIVE` / `POSITIVE` (phân loại văn bản 2 lớp). |
| **Exercise 1** | Dùng model có sẵn `distilbert-base-uncased-finetuned-sst-2-english`: tokenize câu mẫu, phân tích cảm xúc bằng softmax trên logits. |
| **Exercise 2** | Fine-tune `distilbert/distilbert-base-uncased` (66.955.010 tham số, thêm lớp phân loại 2 nhãn) trên bộ `rotten_tomatoes`. |
| **Dữ liệu** | 10.662 câu review phim: train 8.530, validation 1.066, test 1.066; hai nhãn cân bằng 50/50; trung bình 21 từ/câu. |
| **Phương pháp** | Transfer learning: tokenizer WordPiece → DistilBERT (6 lớp Transformer) → lớp phân loại; huấn luyện bằng cross-entropy + AdamW, lr 2e-5, batch 16, 3 epoch, fp16, seed 42; theo dõi validation mỗi epoch, đánh giá test một lần. |
| **Môi trường** | Laptop Windows, GPU RTX 3050 6GB, VS Code + Jupyter, `torch 2.14.1+cu126`, `transformers 5.21.0`. |

**Kết quả chính**

| | Accuracy | F1 | Ghi chú |
|---|---|---|---|
| Trước fine-tune (lớp phân loại ngẫu nhiên) | 45.22% (validation) | — | Không hơn đoán ngẫu nhiên |
| Notebook, model cuối epoch 3 | **84.62%** (test) | **84.67%** | Kết quả chính thức; train 121,8 giây |
| Script `src/`, epoch tốt nhất (epoch 2) | 84.62% (test) | 84.38% | Precision 85.69%, recall 83.11%; 164/1.066 câu sai |

- Fine-tune nâng accuracy từ khoảng 45% lên khoảng 85% chỉ sau 1 epoch (khoảng 40 giây trên GPU).
- Validation loss tăng 0.3450 → 0.4874 từ epoch 2 trong khi accuracy gần như đứng yên: overfitting.
- Exercise 1 đúng với câu có cảm xúc rõ và câu phủ định, nhưng sai câu mỉa mai với độ tin cậy 99.70%.
- Hạn chế: chỉ 2 nhãn (không có trung tính), một model, một cấu hình siêu tham số, chỉ tiếng Anh.

**Trực quan hóa:** mở [`results/data_visualization.html`](results/data_visualization.html) bằng trình duyệt — phân bố nhãn, độ dài câu, từ đặc trưng mỗi lớp, đường loss, accuracy theo epoch, so sánh trước/sau fine-tune, confusion matrix, các câu đoán sai. Tạo lại bằng `python -m src.visualize`.

## Tài liệu

Tổ chức theo `RULES.md` v1.1 của nhóm (§11, §12, §19).


| File | Nội dung |
|---|---|
| [docs/labs3-description.md](docs/labs3-description.md) | Đề bài, 5W1H, input/output, luồng xử lý, bảng đối chiếu từng yêu cầu |
| [docs/problem-definition.md](docs/problem-definition.md) | Phát biểu bài toán: input/output, mục tiêu, tiêu chí đánh giá, giả định, ràng buộc, phạm vi |
| [docs/design.md](docs/design.md) | Thiết kế: sơ đồ kiến trúc, các module, luồng dữ liệu, quyết định thiết kế và phương án đã cân nhắc |
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
├── docs/                          ← 7 file theo RULES.md v1.1 §19 + problem-definition, design (bảng trên)
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
│   ├── demo.py                    ← dự đoán câu bất kỳ
│   └── visualize.py               ← tạo trang HTML trực quan hóa dữ liệu và kết quả
├── data/rotten_tomatoes/          ← train.csv, validation.csv, test.csv (do src.data tạo)
├── models/                        ← model sau fine-tune (không đưa lên GitHub)
└── results/                       ← số liệu, biểu đồ, câu đoán sai, data_visualization.html
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
& $py -m src.visualize       # Trực quan hóa: tạo results/data_visualization.html
```

Máy chỉ có CPU: chạy `$env:LAB3_TRAIN_LIMIT = "2000"` trước `src.train`.

## Lưu ý khi đưa lên GitHub

- Bài nằm ở nhánh **`Lab3`**.
- Không đưa `models/distilbert-rotten-tomatoes/` và `models/checkpoints/` lên (~255 MB, vượt giới hạn 100 MB/file); `.gitignore` đã loại trừ. Khi upload qua web GitHub, tự bỏ các thư mục này.
