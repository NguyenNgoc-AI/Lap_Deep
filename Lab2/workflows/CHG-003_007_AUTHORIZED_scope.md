# CHG-003..007 — Triển khai WF-002

Chỉ thị người dùng: “Thực hiện đến khi xong đi” (2026-10-30).
Được phép tiếp tục trọn phạm vi WF-002, gồm code, tải dataset/weights, thư viện biểu đồ nếu cần, test, 7 run, đánh giá và báo cáo. Không coi đây là phê duyệt AFTER đã được xem; đây là quyền triển khai trực tiếp thay cho việc dừng tại mỗi gate trong phạm vi này.

- CHG-003: phase02 dữ liệu + shared helpers/config + tests dữ liệu. BEFORE: chưa tồn tại.
- CHG-004: phase03 mô hình/preflight + tests. BEFORE: chưa tồn tại.
- CHG-005: phase04 training/resume/TensorBoard + tests. BEFORE: chưa tồn tại.
- CHG-006: phase05 evaluation/report/charts + tests; bổ sung matplotlib nếu thiếu.
- CHG-007: mở rộng notebook điều phối, README và lưu trạng thái/kết quả.

Checkpoint file hiện hữu: history/checkpoints/CHG-003_007_before/. Không sửa phase01 hoặc kết quả WF001. File mới tạo trong workspace; raw giữ nguyên; các checkpoint của cùng run được cập nhật atomically. Không rollback tự động.

Kiểm chứng: unit tests dữ liệu/metrics/resume; preflight batch thật; train 7run đúng config; test cuối sau selection validation; notebook execution, TensorBoard và report. Snapshot AFTER và hash được lưu khi triển khai xong, trước training dài.
