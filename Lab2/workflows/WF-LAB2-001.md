# WF-LAB2-001 v1 · triển khai Practice 2

Ngày 03/11/2026 · Codex · APPROVED / LOCKED. Nguồn thiết kế: docs/labs2-description.md. Gate A: người dùng trả lời “ok” cho WF-LAB2-001. Gate B cùng lượt: CHG-DATA-001.

| Thứ tự | Input → output | Triển khai và nghiệm thu |
|---|---|---|
| P01 Data | Ảnh local → manifest + audit, class mapping, batch | Tận dụng src/phases/phase_02_data.py. Hash nội dung RGB trước khi chia; giữ nguyên test, loại overlap phía development, cách ly development có nhãn xung đột, ghi lý do; phát hiện ảnh hỏng và ghi path. Chia phân tầng theo lớp 80/20 seed 42. Đối soát số lượng, không giao hash giữa split, kiểm tra batch và tính lặp lại. |
| P02 Model | Hai file weights local + batch → model và bảng tham số | src/phases/phase_03_models.py. Kiểm tra key khi nạp, lớp trainable theo docs/model.md, chế độ Dropout/BatchNorm, logits hữu hạn [B,6] và tổng tham số theo stage. |
| P03 Training | Manifest + model → log epoch, TensorBoard, handoff, best.pt, last.pt | src/phases/phase_04_train.py. Hai run chính 5+≤15 epoch. Main LR fine-tuning 1e-5; nhánh VGG 3e-6 chỉ phân tích validation từ cùng handoff và thứ tự mẫu. Kiểm gradient, trọng số khóa, resume, loss weighted, early stopping và nạp lại best theo số đúng/loss/epoch. |
| P04 Evaluation | Best của hai run chính → so sánh validation, khóa lựa chọn, đánh giá test | src/phases/phase_05_evaluate.py. Báo majority và head-only baseline, learning curves, metrics theo lớp, dự đoán từng ảnh, confusion matrix và lỗi. Đối chiếu số đúng và cỡ tập. Ghi giới hạn một seed và test từng được xem. |
| P05 Demo | Best đã khóa + ảnh → nhãn, softmax score, run, epoch | Module demo, dùng mapping/transform đã lưu; đối chiếu một ảnh với inference P04. |

Notebook notebooks/main.ipynb điều phối các phase. Rà config và code cũ theo từng CHG; sao lưu trước khi thay, không ghi đè kết quả lịch sử. Mỗi phase ghi hàm, input/output, log và kết quả thật vào tài liệu tương ứng. Smoke dùng thư mục riêng và ít batch, kiểm cả hai stage. Chỉ chuyển normal khi smoke đạt; xác nhận đủ dung lượng checkpoint trước khi chạy. Không cài dependency, đổi dataset, tuning theo test, hoặc publish. Nếu lỗi thì ghi traceback và dừng tại phase lỗi. Rollback bằng bản BEFORE/backup của đúng CHG khi được duyệt, không thay raw. Hoàn thành khi có bằng chứng từng tiêu chí mô tả, đối chiếu validation sau reload, demo và log thật.

