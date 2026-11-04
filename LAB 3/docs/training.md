# Training — Fine-tune DistilBERT

## 1. Cấu hình huấn luyện

| Tham số | Giá trị | Ghi chú |
|---|---|---|
| Learning rate | 2e-5 | Mức thường dùng khi fine-tune BERT/DistilBERT |
| Batch size train / đánh giá | 16 / 32 | |
| Số epoch | 3 | |
| Weight decay | 0.01 | |
| Max length | 128 token | |
| Optimizer | AdamW | Mặc định của `Trainer` |
| Loss | Cross-entropy | `Trainer` tự dùng cho phân loại |
| Lịch learning rate | Giảm tuyến tính về 0 | Mặc định của `Trainer` |
| `eval_strategy` | `"epoch"` | Đánh giá trên **validation** sau mỗi epoch |
| fp16 | Bật khi có GPU NVIDIA | Nhanh hơn, ít tốn bộ nhớ GPU |
| Seed | 42 | `set_seed(42)` |
| Số bước mỗi epoch | 534 | 8.530 câu / batch 16 |

Transformers 5 dùng tên `eval_strategy` (không còn `evaluation_strategy`) và `processing_class=tokenizer` (không còn `tokenizer=`) khi tạo `Trainer`.

## 2. Notebook và script

| | `notebooks/ex2_finetuning.ipynb` | `src/train.py` |
|---|---|---|
| Theo dõi mỗi epoch | Validation | Validation |
| Lưu checkpoint | Không (`save_strategy="no"`) | Mỗi epoch (`save_strategy="epoch"`, giữ tối đa 2) |
| Model dùng để đánh giá | Cuối epoch 3 | Epoch có validation accuracy cao nhất (`load_best_model_at_end`) |
| Lưu model ra đĩa | Không | `models/distilbert-rotten-tomatoes/` |
| Kết quả ghi ra | Output trong notebook | `results/train_log.json`, `train_history.csv`, `loss_curve.png` |

Script giữ epoch tốt nhất vì các lần chạy trước cho thấy validation loss tăng sau epoch 1 (mục 4).

## 3. Cách chạy

**Notebook:** mở trong VS Code, chọn kernel `.venv`, **Restart Kernel → Run All**.

**Script** (trong thư mục `LAB 3`):

```powershell
D:\Code\.venv\Scripts\python.exe -m src.train
```

Máy chỉ có CPU: đặt `$env:LAB3_TRAIN_LIMIT = "2000"` trước khi chạy để giới hạn số câu train.

## 4. Các lần chạy đã có

| Lần | Ngày | Phiên bản | Thiết bị | Epoch | Số bước | Thời gian train |
|---|---|---|---|---|---|---|
| 1 | 28/10 | Bản đầu (đánh giá trên test) | GPU RTX 3050 6GB | 3 | 1.602 | 118,6 giây |
| 2 | 30/10 | Bản tách validation/test | CPU | 1 (chưa chạy hết) | 534 | 1.177,7 giây (~19,6 phút) |
| 3 | — | Bản hiện tại, chạy lại đủ 3 epoch | GPU | — | — | **`PENDING_UPDATE`** |

**Quá trình học ở lần 1** (loss đánh giá trên test):

| Epoch | Training loss | Loss đánh giá |
|---|---|---|
| 1 | 0.4002 | **0.3625** |
| 2 | 0.2297 | 0.4408 |
| 3 | 0.1447 | 0.5470 |

Training loss giảm đều qua 3 epoch, nhưng loss đánh giá thấp nhất ở epoch 1 rồi tăng → model bắt đầu **overfitting** từ epoch 2. Trên biểu đồ training loss có hai lần giảm mạnh quanh bước 534 và 1.068, đúng lúc bắt đầu epoch 2 và 3 (model gặp lại dữ liệu đã học).

**Lần 2** (bản tách validation/test, 1 epoch): training loss 0.3958, validation loss 0.3569.

Độ chính xác của các lần chạy: xem [evaluation.md](evaluation.md).

## 5. Lưu ý môi trường

- Train trên CPU chậm hơn GPU khoảng 30 lần ở bài này: 1 epoch mất ~19,6 phút trên CPU (lần 2), so với ~40 giây trên RTX 3050 (lần 1: 118,6 giây cho 3 epoch). Hai lần chạy trên hai máy khác nhau nên chỉ là ước lượng.
- PyTorch phải là bản CUDA (`torch.__version__` có đuôi `+cu126`); bản `+cpu` cho `torch.cuda.is_available() == False` dù máy có card NVIDIA.
- Khi cài lại torch trên Windows, phải tắt kernel Jupyter trước, nếu không sẽ báo `Access is denied` với `c10.dll`.
