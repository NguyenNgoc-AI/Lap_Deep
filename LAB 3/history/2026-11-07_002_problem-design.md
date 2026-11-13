# Phiên 2026-11-07_002 · Bổ sung Problem Definition và Design

- **Người thực hiện:** HuHoww, có Claude hỗ trợ. **WF:** không có. **Trạng thái:** DOCS ONLY — không sửa code, notebook hay kết quả.
- **Yêu cầu:** Lab 3 cần thêm phần define problem và design.
- **Tra cứu:** repo nhóm (`LAB-1`, `Lab2`, `lab2.1`) và `RULES.md` v1.1 không có mẫu riêng cho hai phần này → đặt tên theo kiểu các file `docs/` hiện có.

## File

| File | Nội dung |
|---|---|
| `docs/problem-definition.md` (mới) | Bối cảnh; phát biểu bài toán (x → y ∈ {0, 1}, p(y \| x)); mục tiêu; tiêu chí đánh giá và giao thức train/validation/test; giả định; ràng buộc; phạm vi |
| `docs/design.md` (mới) | Sơ đồ kiến trúc (Mermaid); bảng 6 module với đầu vào/đầu ra; thiết kế dữ liệu, model, huấn luyện, đánh giá, demo; 9 quyết định thiết kế kèm phương án khác; yêu cầu phi chức năng; hạn chế |
| `README.md`, `docs/labs3-description.md`, `docs/plan-progress.md`, `PROJECT_STATE.md`, `AI_USAGE.md` | Thêm link và mục theo dõi cho hai file mới |

## Lưu ý

- `design.md` mô tả thiết kế **đã triển khai** (viết sau khi code và kết quả đã có), không phải thiết kế được duyệt trước khi code.
- Mọi số liệu lấy từ kết quả đã chạy (notebook 04/11, script 07/11).
