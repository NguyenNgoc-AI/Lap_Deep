# PROJECT_STATE — Lab 2

Cập nhật: 2026-11-03, Asia/Saigon.
Trạng thái: Đã nhận yêu cầu bắt đầu Generate. Workflow kỹ thuật WF-LAB2-001 và bản code CHG-DATA-001 đang được trình duyệt trong workflows/. Chưa sửa source hoặc chạy smoke/normal. Xem history/2026-11-03_007_generate-review.md.

Description đã bổ sung sáu câu hỏi 5W1H, bảng input/output toàn bài và bảng bàn giao giữa P01–P05.

P02 có bản mô tả kiến trúc và phương án freeze/fine-tune theo từng lớp tại docs/model.md. Chính sách mở khối cuối và chế độ Dropout/BatchNorm là đề xuất đang thảo luận.

P02 đã bổ sung sơ đồ từ ảnh RGB 224×224 đến sáu logits cho từng kiến trúc, kích thước sau mỗi khối và giai đoạn cập nhật trọng số.

P03 có lịch đề xuất trong docs/training.md: mỗi model học classifier 5 epoch rồi fine-tune tối đa 15 epoch, với điều kiện dừng theo validation loss. Cấu hình đang ở bước Description.

## Lần dọn dự án ngày 2026-11-01


Người dùng xác nhận: “xóa đi rồi thảo luận lại từ đầu để làm lại”.
Đã xóa vĩnh viễn đúng năm thư mục trong D:/Lab2: docs, history, outputs, tests, workflows. Đã kiểm tra đường dẫn nằm trực tiếp trong workspace và xác nhận cả năm không còn tồn tại. Không tạo bản lưu trữ thay cho việc xóa.

Giữ nguyên data, src, configs, experiments, notebooks, .venv, requirements.txt, README.md và các file rules. Các file/thư mục khác ngoài năm mục trên không thuộc phạm vi xóa. Notebook có thể còn output nhúng và code cũ; các kết quả đó là lịch sử, không chứng minh cho phương án mới. Notebook/pipeline hiện có tham chiếu tới các artifact đã xóa nên chưa thể coi là chạy hoàn chỉnh.

Tiến trình tối ưu đã được dừng theo yêu cầu trước đó; không chủ động chạy lại. Không khôi phục history/workflows trong lượt dọn này; ghi nhận việc xóa tại đây theo phạm vi người dùng vừa xác nhận.

## Nội dung cần thảo luận trước khi làm lại

1. Yêu cầu giáo viên và cấu trúc DOCX: mỗi phase có mục tiêu, input/output, code, thuật toán, lý do lựa chọn và kết quả.
2. Thiết kế hai thí nghiệm chính cho VGG11 và DenseNet121: cấu hình, giai đoạn transfer/fine-tune, ngân sách epoch, seed và điều kiện so sánh công bằng.
3. Metric chính, ý nghĩa best_val, quy tắc chọn best checkpoint, lưu last checkpoint và early stopping.
4. Log console/file/TensorBoard có cấu hình, thời gian, chỉ số từng epoch và lý do dừng.
5. Quy trình dữ liệu và đánh giá: test cũ đã từng được xem; việc xóa artifact không làm test trở thành holdout mới.

## Bộ quy tắc hiện hành từ ngày 2026-11-02

- `RULES.md` là bản v1.1 từ `PROJECT_RULES_FINAL_v1.1.zip`. Mục 19 quy định bảy tài liệu trong `docs/` và việc cập nhật chúng khi triển khai. `working_rule.md` tiếp tục bổ sung quy tắc cộng tác và ML/AI theo `AGENTS.md`.
- Hai bản v1.0 đã khóa được lưu riêng vì khác nội dung. Bản từng dùng tại Lab2 ở `versions/RULES_v1.0_Lab2_2026-10-29.md`. Bản đi kèm ZIP ở `versions/RULES_v1.0_FINAL_2026-10-29.md`.
- `workflows/WF-RULES-001.md` và bốn nhật ký nhập từ ZIP ghi lại việc ban hành quy tắc. Trạng thái hoàn tất của workflow này chỉ áp dụng cho bộ tài liệu quản trị.
- Tại ngày 02/11, Lab2 đang thảo luận phương án kỹ thuật và chưa khởi tạo bộ `docs/`.
- Nhật ký tích hợp tại Lab2 nằm ở `history/2026-11-02_002_tich-hop-rules-v1.1.md`.
