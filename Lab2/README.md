# Lab 2 · Phân loại ảnh cảnh quan

[Notebook chính](notebooks/main.ipynb) mở kết quả đánh giá và chạy demo ảnh mới. [Description](docs/labs2-description.md) ghi thiết kế; [bảng nghiệm thu](docs/plan-progress.md) liên kết code, log và kết quả cho từng phase.

Chạy từ PowerShell tại D:\Lab2, chọn kernel **Lab2 (.venv)**:

```powershell
.\.venv\Scripts\python.exe -m notebook notebooks/main.ipynb
```

Để dự đoán ảnh riêng, truyền đường dẫn cho demo. Bỏ đối số để chạy ví dụ trong seg_pred. Để xem đường học, mở TensorBoard và truy cập http://127.0.0.1:6006.

```powershell
.\.venv\Scripts\python.exe -m evaluation.demo "D:\duong-dan\anh.jpg"
.\.venv\Scripts\python.exe -m tensorboard.main --logdir outputs/training-scene-v1 --host 127.0.0.1 --port 6006
```

Hai run chính dùng cùng manifest, học classifier 5 epoch rồi fine-tune tối đa 15 epoch. DenseNet121 epoch 9 được chọn trên validation và dùng cho cả test lẫn demo. Xem [huấn luyện](docs/training.md), [đánh giá](docs/evaluation.md) và [demo](docs/demo.md).
