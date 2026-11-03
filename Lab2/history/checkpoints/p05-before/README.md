# Lab 2 — Intel Image Classification (chạy local)

Workspace: `D:\Lab2`. Python riêng: `.venv\Scripts\python.exe`; GPU Intel Arc dùng PyTorch XPU. Workflow và ngoại lệ dữ liệu được ghi trong `workflows/`, nhật ký trong `history/`.

## Mở notebook

Trong PowerShell tại `D:\Lab2`:

```powershell
.\.venv\Scripts\python.exe -m notebook notebooks/main.ipynb
```

Chọn kernel **Lab2 (.venv)**. Notebook điều phối các phase 02–05; có thể chọn một phase, khoảng phase hoặc toàn pipeline. Restart kernel sau khi sửa source. Các run hoàn tất chỉ được dùng lại nếu fingerprint khớp; run bị ngắt tiếp tục từ epoch hoàn chỉnh gần nhất. Không xóa thư mục outputs để thử lại một cách tùy tiện.

## Chạy bằng terminal

```powershell
.\.venv\Scripts\python.exe -u -m src.phases.phase_02_data
.\.venv\Scripts\python.exe -u -m src.phases.phase_03_models
.\.venv\Scripts\python.exe -u -m src.phases.phase_04_train
.\.venv\Scripts\python.exe -u -m src.phases.phase_05_evaluate
```

Ma trận: VGG11 và DenseNet121, mỗi kiến trúc 3 cấu hình (LR 0.001/batch8; LR 0.0003/batch8; LR 0.001/batch16), 5 epoch/run; R07 fine-tune block cuối của run thắng thêm 3 epoch LR 0.00001. Chọn bằng validation trước test. Không chạy đồng thời notebook và CLI training.

## TensorBoard

```powershell
.\.venv\Scripts\python.exe -m tensorboard.main --logdir outputs/experiments --host 127.0.0.1 --port 6006
```

Mở <http://127.0.0.1:6006>. Các scalar: `train/loss`, `train/accuracy`, `validation/loss`, `validation/accuracy`, thời gian theo epoch.

## Kết quả và kiểm thử

- Báo cáo: `outputs/report/report.md`; bảng: `experiments.csv`, `epoch_metrics.csv`, `test_metrics.csv`, `per_class_metrics.csv`.
- Hình: `learning_curves.png`, confusion matrix từng run được đánh giá.
- Checkpoint: `outputs/experiments/Rxx/best.pt`, `last.pt`; metadata/RNG/optimizer được lưu để resume. Chỉ nạp checkpoint tin cậy do project tạo.
- Dữ liệu raw bất biến: `data/raw/intel-v2`; manifest và audit: `outputs/data/`.
- Trọng số ImageNet: `data/weights/checkpoints`; checksum/URL: `outputs/models/weights.json`.
- Kiến trúc và tham số trainable: `outputs/models/`.
- Notebook đã chạy: `outputs/notebooks/main.executed.ipynb` (tạo sau khi hoàn tất pipeline).

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Dataset v2 có 13 nhóm trùng byte nhưng khác nhãn: loại 23 ảnh train liên quan khỏi manifest, giữ nguyên test/raw; tổng 28 ảnh train bị loại kể cả các trường hợp trùng khác. Xem `workflows/WF-002_AMENDMENT-01_label-conflicts.md`. Một seed và 5+3 epoch chỉ phục vụ bài thực hành, chưa phải so sánh thống kê trên nhiều seed.

Phân tích đề và gợi ý trình bày: [docs/phan_tich_de.md](docs/phan_tich_de.md). Nhận xét số liệu thực, các cặp lớp dễ nhầm và dấu hiệu cần theo dõi: [docs/nhan_xet_ket_qua.md](docs/nhan_xet_ket_qua.md).
