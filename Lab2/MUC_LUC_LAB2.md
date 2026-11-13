# Mục lục file Lab 2

**[Báo cáo Word](docs/bao-cao-lab2.docx)** · **[Bài thuyết trình PowerPoint](docs/overview.pptx)** · **[Dashboard HTML](docs/data-visualization.html)** · **[Notebook trình bày 16 bước](notebooks/lab2_pipeline.ipynb)**

Các liên kết bên dưới đi theo 10 phần của báo cáo. Đường dẫn tính từ thư mục gốc của Lab 2. Các file trọng số `.pt` trong mục 7 nằm trong bản dự án trên máy.

## 1. Tổng quan dự án

- [Định nghĩa bài toán, đầu vào và đầu ra](docs/labs2-description.md)
- [Quy trình P01–P05](workflows/WF-LAB2-001.md) · [Kết quả kiểm chứng từng phase](docs/plan-progress.md)

## 2. Tổng quan dữ liệu

- [Mô tả dữ liệu](docs/data.md) · [Bảng chia train, validation và test cuối cùng](outputs/scene-review/report.md)
- [Manifest từng ảnh](outputs/data/manifest.csv) · [Danh sách ảnh bị loại và lý do](outputs/data/excluded.csv)
- [Mã tạo manifest theo nhóm cảnh](outputs/scene-review/build_manifest.py) · [Mã đọc và tiền xử lý ảnh](src/phases/phase_02_data.py)

## 3. Phân tích khám phá dữ liệu

- [Báo cáo EDA ban đầu](outputs/eda-seed42/EDA.md) · [Notebook EDA](notebooks/eda.ipynb) · [Các biểu đồ EDA trên dashboard](docs/data-visualization.html#eda)
- [Phân bố lớp](outputs/eda-seed42/phan-bo.png) · [Kích thước ảnh](outputs/eda-seed42/kich-thuoc-train.png) · [Chất lượng ảnh](outputs/eda-seed42/chat-luong-train.png)
- [Các cặp ảnh nghi gần trùng](outputs/eda-seed42/near-pairs.csv) · [Kết quả rà từng cặp](outputs/scene-review/review.csv)

## 4. Mô hình

- [So sánh kiến trúc VGG11 và DenseNet121](docs/model.md) · [Mã dựng model và đóng băng tham số](src/phases/phase_03_models.py)
- [Số tham số theo giai đoạn](outputs/models/preflight.json) · [Kiểm tra các lớp thực sự được cập nhật](outputs/models/stage-checks.json)

## 5. Huấn luyện

- [Lịch huấn luyện hai giai đoạn](docs/training.md) · [Mã huấn luyện và dừng sớm](src/phases/phase_04_train.py) · [Bảng kết quả các run](outputs/training-scene-v1/TRAINING.md)
- [Log console toàn phiên](outputs/training-scene-v1/console.log) · [Log thời gian VGG11](outputs/training-scene-v1/vgg11/run.log) · [Log thời gian DenseNet121](outputs/training-scene-v1/densenet121/run.log)

## 6. Validation

| Model | Accuracy và loss theo epoch | Đường học | Validation sau khi nạp lại checkpoint |
|---|---|---|---|
| VGG11 | [Lịch sử 10 epoch](outputs/training-scene-v1/vgg11/history.json) | [Biểu đồ](outputs/training-scene-v1/vgg11/curves.png) | [Kết quả](outputs/training-scene-v1/vgg11/result.json) |
| DenseNet121 | [Lịch sử 12 epoch](outputs/training-scene-v1/densenet121/history.json) | [Biểu đồ](outputs/training-scene-v1/densenet121/curves.png) | [Kết quả](outputs/training-scene-v1/densenet121/result.json) |

## 7. Chọn checkpoint

Trong hai run này, epoch có train accuracy cao nhất trùng với epoch cuối, nên trọng số tương ứng nằm trong `last.pt`. Checkpoint dùng để so sánh hai model là `best.pt`, được chọn bằng validation.

| Model | Best val | Best train trong lần chạy này | Chuyển sang fine-tuning |
|---|---|---|---|
| VGG11 | [Epoch 7 · best.pt](outputs/training-scene-v1/vgg11/best.pt) | [Epoch 10 · last.pt](outputs/training-scene-v1/vgg11/last.pt) | [Epoch 4 · handoff.pt](outputs/training-scene-v1/vgg11/handoff.pt) |
| DenseNet121 | [Epoch 9 · best.pt](outputs/training-scene-v1/densenet121/best.pt) | [Epoch 12 · last.pt](outputs/training-scene-v1/densenet121/last.pt) | [Epoch 4 · handoff.pt](outputs/training-scene-v1/densenet121/handoff.pt) |

## 8. Chọn model

- [Quyết định chọn DenseNet121 bằng validation](outputs/training-scene-v1/report.json)
- [Kết quả nhánh thử learning rate của VGG11](outputs/training-scene-v1/vgg11-lr-ablation/result.json) · [Biểu đồ so sánh hai learning rate](outputs/training-scene-v1/vgg11-lr-comparison.png)

## 9. Đánh giá trên tập test

- [Báo cáo đánh giá DenseNet121](outputs/evaluation-scene-v1/report.md) · [Metrics tổng hợp](outputs/evaluation-scene-v1/metrics.json) · [Precision, recall và F1 từng lớp](outputs/evaluation-scene-v1/per-class.csv)
- [Ma trận nhầm lẫn](outputs/evaluation-scene-v1/confusion.png) · [Dự đoán từng ảnh](outputs/evaluation-scene-v1/predictions.csv) · [Danh sách ảnh dự đoán sai](outputs/evaluation-scene-v1/errors.csv)

## 10. Triển khai và chạy demo

- [Hướng dẫn chạy tại máy](README.md) · [Notebook điều phối](notebooks/main.ipynb) · [Thư viện cần thiết](requirements.txt)
- [Mã đánh giá](evaluation/scene.py) · [Mã dự đoán một ảnh](evaluation/demo.py) · [Hướng dẫn thay ảnh đầu vào](docs/demo.md)
- [Kết quả demo ảnh 10004.jpg](outputs/demo-scene-v1/result.json) · [Đối chiếu dự đoán demo với bước đánh giá](outputs/smoke-p05/check.json)
