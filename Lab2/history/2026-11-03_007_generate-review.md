# Generate · 03/11/2026 · đề xuất đầu tiên

Đã đọc rules, trạng thái, description và log 006. Dự án có code cũ xử lý ảnh và chia phân tầng trong src/phases/phase_02_data.py. Hash cũ dựa trên byte của file. Hai file trọng số hiện có trong data/weights/checkpoints. Root không có .git; cần backup file gốc trước thay đổi.

WF-LAB2-001 v1 UNDER_REVIEW. CHG-DATA-001: thêm hàm hash RGB và thay biểu thức sha256(path) ở inspect_images bằng rgb_digest(image). Chi tiết BEFORE/AFTER ở workflows/CHG-DATA-001.md. Giữ logic chọn test và chia split hiện có. Các thay đổi audit ảnh hỏng, ghi lý do, model/train/eval/demo được rà theo từng CHG sau.

Chưa sửa source, chưa chạy smoke/normal, chưa tạo metrics. Chưa khóa WF hoặc chấp thuận CHG. Khi áp dụng, kiểm thử ảnh cùng pixel khác metadata, khác shape, và kiểm hash không chồng lấn giữa split. Log này không thay cho bằng chứng chạy.
