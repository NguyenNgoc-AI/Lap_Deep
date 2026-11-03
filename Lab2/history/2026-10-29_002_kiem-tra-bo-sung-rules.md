# Nhật ký 002 — Kiểm tra thiếu sót PROJECT RULES v1.0-draft

- Ngày: 2026-10-29 (Asia/Ho_Chi_Minh)
- Loại công việc: **Rà soát, phản biện, đề xuất**; không triển khai mã nguồn.
- Trạng thái: **ĐÃ RÀ SOÁT — ĐỀ XUẤT CHỜ DUYỆT**.
- Nguồn đã kiểm tra: `project_rules/RULES.md` (10 mục, 0–10; phiên bản 1.0-draft).
- File mã nguồn được thay đổi: **Không có**.
- File Rules được thay đổi: **Không có**.
- File mới của lần này: `project_rules/history/2026-10-29_002_kiem-tra-bo-sung-rules.md`.
- Workflow: chưa có workflow triển khai nào được phê duyệt; công việc hiện tại là đánh giá nội dung Rules theo yêu cầu. Không triển khai các đề xuất.

## I. Các điểm đã có trong Rules hiện tại

1. Trình bày WHAT/WHERE/WHY/HOW/IMPACT/VERIFY trước thao tác.
2. Mỗi thay đổi code có BEFORE/AFTER trên chat từ file thực tế.
3. Notebook điều phối; logic từng phase đặt trong module `.py`.
4. Workflow được duyệt thì khóa; thay đổi ngoài phạm vi phải trình duyệt workflow khác.
5. Nhật ký Markdown theo từng lần làm việc, bao gồm quyết định, code, test, lỗi.
6. Phản biện bắt buộc, checklist kiểm soát trước/sau.

## II. Những lỗ hổng và đề xuất bổ sung (CHƯA ĐƯỢC DUYỆT)

### P1. Hai tầng phê duyệt riêng biệt — CRITICAL

**Phát hiện:** Mục 2 và 4 nói có phê duyệt nhưng chưa chuẩn hóa rõ hai cổng độc lập. Có thể nhầm việc chốt workflow là được phép ghi mọi code trong workflow.

**Đề xuất quy tắc:**

- GATE A — Phê duyệt workflow: chốt phạm vi, bước, I/O, tiêu chí thành công. Chỉ cho phép chuẩn bị đề xuất code trong phạm vi ấy.
- GATE B — Phê duyệt CHANGE ID: trình file/vị trí, BEFORE và AFTER chính xác, kiểm thử/ảnh hưởng; chỉ được ghi khi người dùng duyệt thay đổi đó.
- Nếu người dùng duyệt một phần, chỉ thực hiện phần được duyệt. Không coi im lặng là đồng ý. Thay đổi sau khi duyệt GATE B phải trình lại để duyệt.

### P2. Version Control, snapshot, rollback — CRITICAL

**Phát hiện:** Có nhắc khả năng khôi phục nhưng không có chuẩn ghi nhận phiên bản trước/sau, cách rollback và giới hạn thao tác nguy hiểm.

**Đề xuất quy tắc:**

- Trước sửa: ghi lại Git commit/hash hiện tại (nếu có), trạng thái working tree, file diff và các tệp chưa commit bị ảnh hưởng; không ghi đè công việc chưa được lưu của người dùng.
- Mỗi thay đổi có CHANGE ID, bản sao/diff kiểm chứng được, điểm khôi phục và kế hoạch rollback.
- Không được tự ý `reset --hard`, xóa file, ghi đè dữ liệu hoặc rollback thay đổi của người dùng khi chưa được duyệt riêng.
- Nếu chưa có Git, phải báo và thống nhất chiến lược backup tối thiểu trước thay đổi có rủi ro.

### P3. Đồng bộ và khôi phục trạng thái làm việc — CRITICAL

**Phát hiện:** Rules/log rời rạc không bảo đảm một cuộc trò chuyện mới biết những gì đã chốt.

**Đề xuất quy tắc:**

- Có `PROJECT_STATE.md` (hoặc file trạng thái tương đương) chứa: Rules version đang hiệu lực; danh sách workflow ID/version/trạng thái/đường dẫn; phase status; các CHANGE ID chính; commit gần nhất; blockages; phần chưa chốt; nhiệm vụ tiếp theo.
- Mỗi phiên bắt đầu bằng việc đọc Rules bản đang hiệu lực, workflow liên quan, trạng thái dự án và các nhật ký gần nhất đang có sẵn. Nếu thiếu quyền truy cập, dừng việc chỉnh sửa và yêu cầu cung cấp tài liệu cần thiết.
- Chỉ những quyết định được người dùng xác nhận mới mang nhãn `APPROVED`; đề xuất chưa duyệt luôn ở `PENDING`.
- Chat không được xem là nguồn trạng thái bền vững duy nhất. Không tuyên bố có thể tự duy trì trạng thái xuyên mọi cuộc trò chuyện nếu chưa có dữ liệu/khả năng truy cập thực tế.

### P4. Definition of Done / nghiệm thu phase — CRITICAL

**Phát hiện:** Quy tắc tiêu chí nghiệm thu có trong workflow nhưng chưa định nghĩa tối thiểu với sản phẩm đầu ra một phase.

**Đề xuất quy tắc:** Một phase chỉ được đánh dấu `COMPLETED` khi: code đúng workflow khóa và đã duyệt; kiểm thử input chuẩn, lỗi và trường hợp biên đạt tiêu chí; output khớp contract; tích hợp được với phase kế; notebook hiển thị trạng thái/nguồn/lỗi chính xác; nhật ký và bằng chứng test đầy đủ; người dùng xác nhận nghiệm thu nếu workflow yêu cầu. Phân biệt `IMPLEMENTED`, `TESTED`, `ACCEPTED`.

### P5. Input/Output Contract + data lineage — HIGH

**Đề xuất quy tắc:** Mỗi phase mô tả rõ input/output schema (kiểu dữ liệu, shape, đơn vị, định dạng, encoding, null, đường dẫn), preconditions/postconditions, lỗi có thể phát sinh, dependency, nguồn dữ liệu và khả năng chạy lại độc lập. Mọi thay đổi contract cần phân tích phase downstream và duyệt trước khi sửa.

### P6. Notebook debug, cell trạng thái và tránh stale results — HIGH

**Đề xuất quy tắc:** Notebook có cell init môi trường, manifest phase, hiển thị source *thực tế* theo yêu cầu, điều khiển chạy từng phase/full pipeline, summary trạng thái, tracebacks và output được kiểm chứng. Không dùng kết quả cell cũ làm bằng chứng sau khi sửa `.py` hoặc đổi input; cần reload/restart kernel/rerun tương ứng. Chỉ log nội dung an toàn; không in token/secret.

### P7. Tái lập kết quả — HIGH

**Đề xuất quy tắc:** Ghi Python version, dependency/lockfile, seed ngẫu nhiên khi có, config không nhạy cảm, đầu vào và phiên bản dữ liệu, resource/dung lượng/cấu hình phần cứng nếu tác động kết quả. Test có dữ liệu nhỏ, deterministic khi khả thi và lệnh chạy tái lập được. Không sửa môi trường hoặc cài package nếu chưa được duyệt.

### P8. Bảo vệ dữ liệu, quyền truy cập và thao tác phá hủy — HIGH

**Đề xuất quy tắc:** Phân biệt dữ liệu gốc và dữ liệu sinh ra; giữ nguyên dữ liệu gốc, ghi outputs ở nơi riêng; không ghi đè/xóa tập dữ liệu hoặc chạy tác vụ tốn chi phí/ảnh hưởng hệ thống ngoài phạm vi khi chưa được duyệt. Secrets phải quản lý bằng phương án an toàn, không chép vào chat, notebook output, Git hay nhật ký; file/log nên loại trừ thông tin nhạy cảm.

### P9. Truy xuất từ yêu cầu đến nghiệm thu — MEDIUM

**Đề xuất quy tắc:** Gắn ID cho `REQ`, `WF`, `CHG`, `TEST`, `LOG`. Mỗi log liên kết yêu cầu -> workflow khóa -> change -> file/cell -> test -> result -> quyết định. Giữ các workflow và bản Rules đã chốt bất biến; nếu cần thay đổi, tạo phụ lục/workflow mới có liên kết và phê duyệt, không sửa nội dung đã khóa.

### P10. Phạm vi được phép làm khi chưa duyệt — MEDIUM

**Phát hiện:** Câu "trước bất kỳ phần nào" có thể gây vòng lặp: ngay cả nghiên cứu hoặc viết workflow cũng cần workflow đã phê duyệt.

**Đề xuất quy tắc:** Các hoạt động chỉ-đọc (kiểm tra file, phân tích, phản biện, viết đề xuất workflow, trình code BEFORE/AFTER) được phép để chuẩn bị phê duyệt. Mọi thao tác thay đổi source, notebook, config, dataset hoặc workflow khóa đều phải qua cổng duyệt. Việc tạo nhật ký theo Rules là ngoại lệ đã cho phép nhưng phải công bố.

### P11. Quản lý ngoại lệ và workflow không thể tiếp tục — MEDIUM

**Đề xuất quy tắc:** Workflow đã phê duyệt giữ nguyên tuyệt đối. Khi có lỗi thiết kế/rủi ro bảo mật hoặc thay đổi nhu cầu, dừng ở điểm phát hiện; ghi `BLOCKED`, trình nguyên nhân, ảnh hưởng, phương án xử lý bằng workflow bổ sung riêng. Nếu người dùng duyệt quy trình mới, lưu cả hai tài liệu và quan hệ thay thế/bổ sung; không tự ý sửa bản gốc.

### P12. Tiêu chuẩn nhật ký và bảo vệ nhật ký — MEDIUM

**Đề xuất quy tắc:** Mỗi phiên làm việc/turn có thể xác định ranh giới rõ ràng; log chứa cả quyết định đã chốt và chưa chốt, kiểm thử không thực hiện, vị trí file thực tế và tham chiếu diff. Không đưa bí mật, dữ liệu nhạy cảm hoặc quá nhiều output vô ích vào log. Có trạng thái `LOCAL_ONLY` nếu chưa đồng bộ vào repo. Nếu công cụ không thể ghi file, phải thông báo thay vì giả vờ hoàn tất.

## III. Khuyến nghị ưu tiên triển khai vào Rules

- **Bắt buộc trước chốt v1.0:** P1, P2, P3, P4.
- **Nên chốt cùng v1.0:** P5, P6, P7, P8.
- **Làm rõ để Rules không tự mâu thuẫn:** P9, P10, P11, P12.

## IV. Phản biện đáng chú ý

1. Workflow bất biến giúp tránh phạm vi trôi nhưng không thể ép chạy tiếp khi phát hiện nguy cơ/thiết kế lỗi; cách đúng là dừng và xin phê duyệt workflow bổ sung, không sửa lén bản cũ.
2. OOP là cách tổ chức, không phải mục tiêu; module Python độc lập và contract rõ ràng quan trọng hơn việc tạo class cho mọi phase.
3. Hiển thị toàn bộ source của phase có thể rất dài hoặc lộ secrets; cho phép chỉ định phần cần xem và có nguyên tắc che thông tin nhạy cảm, vẫn bảo đảm BEFORE/AFTER chính xác với phần sửa.
4. Lưu log theo "mọi lần làm việc" cần định nghĩa ranh giới phiên và luôn phân biệt việc đề xuất với việc triển khai; tránh log nhầm trạng thái.
5. Không thể cam kết kỹ thuật sẽ không bao giờ lệch Rules trong mọi môi trường. Cơ chế khả thi là Rules nằm trong repo/Project, checklist trước-sau, trạng thái workflow, evidence và dừng khi thiếu điều kiện.

## V. Kiểm thử và thay đổi thực tế

- Kiểm tra đã thực hiện: mở file `RULES.md`, đọc đủ mục 0–10; so với yêu cầu người dùng và các tình huống phát triển notebook nhiều phase.
- Code BEFORE/AFTER: **Không áp dụng vì không có thay đổi mã nguồn.**
- Test chạy: **Không có; đây là rà soát quy trình, không phải thực thi pipeline.**
- Quyết định đã chốt trong lượt này: **Chưa có đề xuất bổ sung nào được người dùng chốt**.
- Bước tiếp theo chờ người dùng: quyết định giữ, sửa hoặc phê duyệt các đề xuất trước khi cập nhật `RULES.md`.
