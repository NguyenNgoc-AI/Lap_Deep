# WF-RULES-001 — Bổ sung quy tắc tài liệu `/docs`

- **Ngày phê duyệt:** 2026-11-02 (Asia/Ho_Chi_Minh)
- **Gate A:** APPROVED — người dùng xác nhận “Duyệt WF-RULES-001.”
- **Gate B:** APPROVED — “Duyệt CHG-RULES-001 đến CHG-RULES-004.”
- **Trạng thái kế hoạch:** LOCKED; triển khai tài liệu quản trị đã hoàn tất.
- **Quyết định tên file:** `plan-progress.md` (không dùng `.sta`).

## Mục tiêu và phạm vi

Bổ sung quy tắc tạo và cập nhật thư mục `docs/` theo bộ Markdown đã chốt. Trong workflow này **chỉ thay đổi tài liệu quản trị**, không tạo notebook, module Python, data, model, hoặc các file `docs/` trong repository đồ án chưa được cung cấp.

## Các bước đã được duyệt (không thay đổi sau khóa)

1. Đọc Rules v1.0 và trạng thái hiện tại; đối chiếu phần được duyệt.
2. CHG-RULES-001: tăng version Rules từ 1.0 lên 1.1 và thêm lịch sử cập nhật.
3. CHG-RULES-002: thêm cây thư mục `docs/` vào cấu trúc gợi ý.
4. CHG-RULES-003: thêm Rule 19, mô tả 7 file Markdown tối thiểu và đồng bộ docs với code.
5. CHG-RULES-004: cập nhật điều khoản thi hành theo bộ tài liệu chuẩn.
6. Lưu bản cũ, cập nhật trạng thái, tạo log và kiểm tra tính chính xác của thay đổi.

## Input / output / kiểm tra

- Input: bản Rules v1.0 đã khóa, PROJECT_STATE v1.0 và phê duyệt của người dùng.
- Output: RULES v1.1, PROJECT_STATE tương ứng, backup Rules v1.0, LOG riêng.
- Kiểm tra: version đúng; `docs/` gồm đúng 7 tên file đã chốt; Rule 19 tồn tại; điều khoản thi hành cập nhật; không sửa mã nguồn đồ án.
- Phương án khôi phục: dùng `versions/RULES_v1.0_FINAL_2026-10-29.md` nếu người dùng duyệt rollback; log mới được lưu lại.

## Quyết định và giới hạn

- APPROVED: bốn CHG được nêu; tên `plan-progress.md`.
- OUT OF SCOPE: tạo hồ sơ docs thực tế và triển khai code cho đồ án; những việc này cần workflow kiến trúc riêng.
- Workflow đã khóa không được sửa đè; thay đổi tương lai cần workflow khác.
