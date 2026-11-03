# Quy tắc làm việc tại Lab2

Phạm vi: D:/Lab2. Bổ sung ngày 2026-11-01 theo yêu cầu người dùng.

Trước khi xử lý công việc, đọc:

1. `RULES.md`: bản v1.1 đã khóa, nhập từ `PROJECT_RULES_FINAL_v1.1.zip`. Bản v1.0 từng dùng tại Lab2 được lưu ở `versions/RULES_v1.0_Lab2_2026-10-29.md`.
2. `working_rule.md`: bản nguyên văn working_rule (2).md, bổ sung quy tắc cộng tác và ML/AI.
3. `PROJECT_STATE.md` cùng workflow và nhật ký liên quan đến yêu cầu hiện tại.

Áp dụng cả hai bộ rules trong phạm vi phù hợp, tuân thủ hướng dẫn hệ thống/công cụ và chỉ thị trực tiếp của người dùng. Rules mới bổ sung, không sửa hay thay thế bản rules cũ đã khóa. Các quy định riêng về workflow, checkpoint, kiểm chứng và nhật ký của Lab2 tiếp tục áp dụng.

Xác định yêu cầu, phạm vi và kế hoạch trước khi sửa; tận dụng phê duyệt đã có trong cuộc hội thoại cho đúng phạm vi, không yêu cầu duyệt lặp lại. Khi thiếu thông tin thiết yếu hoặc có xung đột ảnh hưởng quyết định chưa được người dùng giải quyết, trình bày cụ thể để làm rõ.

Giao tiếp tiếng Việt, phân tích có bằng chứng, không sáo rỗng hoặc bịa kết quả. Bảo vệ code ổn định và thay đổi của người dùng; không tự thêm dependency hoặc mở rộng phạm vi. Với ML, xác định metric, baseline, lý do chọn model, trade-off và cách đánh giá. Không thêm comment/icon thừa; phần giải thích Markdown trong notebook vẫn phục vụ yêu cầu học tập của người dùng.

Sau ba lần thất bại với cùng hướng xử lý, tổng hợp bằng chứng và xem lại nguyên nhân trước khi chọn hướng tiếp theo. Các bước kiểm tra backend/API chỉ áp dụng khi công việc thực sự liên quan backend/API.

Các chữ ký lịch sử, đường dẫn macOS, cấu hình Nx và tham chiếu `.agents/`, `.claude/`, `.cursor/`, `.gemini/` trong working_rule.md thuộc bối cảnh tài liệu nguồn. Không coi chúng là bằng chứng đã đọc file hoặc đã cài cấu hình tại Lab2; không tự tạo/cài các thành phần đó. Chỉ truyền rules cho subagent nếu có sử dụng hợp lệ; tài liệu này không yêu cầu tự khởi chạy subagent.

Không tự sửa nội dung rules đã lưu. Nếu cần thay đổi quy tắc, ghi đề xuất và nguồn phê duyệt riêng, bảo tồn bản trước.
