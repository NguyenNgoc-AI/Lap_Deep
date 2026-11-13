# Đối chiếu dashboard với TensorBoard

Người dùng hỏi về công cụ thay TensorBoard. Đã đọc các mục quality và logs của docs/data-visualization.html, phần SummaryWriter trong src/phases/phase_04_train.py và lệnh trong README.md. Xác nhận file sự kiện tồn tại ở cả ba run thuộc outputs/training-scene-v1. Dashboard là bản xem kết quả đã lưu, có bảng 10 và 12 epoch cho hai run chính. Khi train, code hiện hành ghi sáu chỉ số bằng SummaryWriter. Phiên này chỉ kiểm tra hiện trạng của WF-LAB2-001, không mở server hoặc chạy training.
