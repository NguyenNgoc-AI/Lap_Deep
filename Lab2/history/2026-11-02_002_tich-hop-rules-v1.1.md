# Tích hợp bộ quy tắc v1.1 vào Lab2

Phiên 2026-11-02_002, Asia/Saigon. Hoàn tất phần tài liệu quản trị theo yêu cầu trực tiếp của người dùng về việc bổ sung ZIP và lược bỏ file liên quan đã có. Không có thay đổi kỹ thuật cần GATE A/B. Các phê duyệt trong WF-RULES-001 thuộc lịch sử ban hành bộ quy tắc.

## Nguồn và xử lý trùng

Nguồn là `PROJECT_RULES_FINAL_v1.1.zip` trong Downloads, SHA-256 `5FF45F24FEFD500D45C78594E7B45631A3350255782386F5D8CD5AF4918A4FBA`. Đã đối chiếu các file quản trị ở thư mục gốc với tám mục trong ZIP. Thư mục gốc Lab2 không phải Git repository. Thư mục xuất bản riêng `.publish-repo/` nằm ngoài phạm vi.

- `RULES.md` chuyển từ v1.0 sang v1.1 nguyên bản. Bản cũ tại Lab2 được lưu nguyên byte ở `versions/RULES_v1.0_Lab2_2026-10-29.md` để có thể khôi phục. Bản v1.0 trong ZIP có thêm dòng ghi căn cứ phê duyệt, được lưu riêng ở `versions/RULES_v1.0_FINAL_2026-10-29.md`.
- Nhập nguyên văn `workflows/WF-RULES-001.md` cùng bốn nhật ký từ ZIP vào `history/` (ba phiên ngày 2026-10-29 và phiên 001 ngày 2026-11-02).
- Chỉ cập nhật mục 1 trong danh sách đọc của `AGENTS.md`. Dòng cũ là “1. `RULES.md`: bản nguyên văn Rules_29-10.md v1.0 đã khóa.” Bản mới trỏ tới v1.1 và đường dẫn lưu bản v1.0 của Lab2.
- Gộp thông tin quản trị vào `PROJECT_STATE.md` bằng cách cập nhật ngày từ 2026-11-01, đổi tiêu đề “Thao tác theo chỉ thị trực tiếp” thành tiêu đề ghi ngày dọn dự án và thay đoạn kết bằng mục về bộ quy tắc. Đoạn kết cũ là “Rules tham chiếu: AGENTS.md, RULES.md, working_rule.md. Chưa có workflow mới được chốt. Không tự tiếp tục các workflow hoặc sweep cũ.” Giữ thông tin kỹ thuật và các câu hỏi đang mở của Lab2.
- Giữ `working_rule.md` vì có quy định cộng tác và ML/AI riêng. Không cần lưu thêm một bản ZIP trong Lab2.

## Kiểm chứng

Đã dùng `Get-FileHash` (SHA-256) đối chiếu dữ liệu đọc từ từng mục ZIP với file đích. Cả bảy file nhập nguyên văn đều khớp. `RULES.md` v1.1 có hash `0D8ACBB8A093514552314A85F735CDCC988A2221A9D0F5FB184E9411234CC3FB`. Bản v1.0 lưu từ Lab2 khớp hash trước khi thay ở thư mục gốc (`9C287F7BFD333EE25A11ADBEFB30AFC5305FF33DCACF39B1A334F9BA8D439BBB`). Hash của `working_rule.md` trước và sau giống nhau.

Đã đọc lại trạng thái sau khi gộp. Phương án kỹ thuật vẫn đang thảo luận. Việc tạo bộ tài liệu trong `docs/` và chạy thí nghiệm nằm ngoài yêu cầu nhập gói.
