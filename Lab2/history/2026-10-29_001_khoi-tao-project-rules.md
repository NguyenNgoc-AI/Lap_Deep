# Nhật ký làm việc — Khởi tạo PROJECT RULES

- **Ngày:** 2026-10-29
- **Session ID:** 2026-10-29-001
- **Trạng thái:** Đã tạo bản nháp quy tắc; **chờ người dùng duyệt**, chưa khóa.
- **Workflow áp dụng:** Chưa có workflow đã duyệt. Hạng mục hiện tại là soạn thảo đề xuất Rules theo yêu cầu trực tiếp; không sửa mã nguồn dự án.

## 1. Mục tiêu của lần làm việc

Viết bộ quy tắc vận hành cho toàn bộ đồ án, chuyển sáu yêu cầu của người dùng thành các bước kiểm soát cụ thể, dễ rà soát và có thể thực hiện trong các lượt làm việc tiếp theo.

## 2. Các yêu cầu người dùng đưa ra

1. Trước khi làm cần thông báo sẽ làm gì, sửa ở đâu, sửa như thế nào; hiển thị code trước và sau riêng biệt ngay trên chat để người dùng kiểm tra.
2. Notebook là điểm chạy chính và có cơ chế hiển thị source từng phần để debug nhanh; logic chia thành các phase ở các file Python nhỏ, tổ chức kiểu module/OOP.
3. Mỗi hạng mục có workflow và chỉ được triển khai sau khi người dùng đồng ý; workflow đã duyệt không được thay đổi về sau.
4. Sau mỗi lần làm việc phải có file `.md` nêu đầy đủ việc làm, code thêm/sửa, nội dung đã bàn, quyết định đã chốt, các vấn đề đã phát sinh; lưu vào một folder riêng phục vụ vibe coding.
5. AI phải tự phản biện với ý kiến của người dùng và thẩm định kỹ ý định thay đổi của chính mình.
6. Viết thành Rules và có cơ chế giúp giữ nhất quán, không đi chệch quy tắc.

## 3. Nội dung đã soạn

- Tạo `RULES.md`, trạng thái `DRAFT`, quy định thứ tự phê duyệt, workflow bất biến, cách xử lý yêu cầu mới, code trước/sau, kiến trúc notebook/phase, nhật ký sau mỗi lần làm, phản biện và checklist ngăn vi phạm.
- Tạo thư mục `history/` làm nơi lưu nhật ký `.md` riêng theo từng lần làm việc.
- Chỉ đưa ra **cấu trúc repo minh họa**, chưa tạo/sửa file code hay notebook nào.

## 4. File được tạo và thay đổi

| File | Trước | Sau | Trạng thái |
|---|---|---|---|
| `RULES.md` | Chưa tồn tại | Tạo bản dự thảo PROJECT RULES v1.0-draft; toàn bộ quy định chi tiết xem file | Đã tạo file nháp |
| `history/2026-10-29_001_khoi-tao-project-rules.md` | Chưa tồn tại | Tạo nhật ký yêu cầu, phạm vi, nội dung, quyết định, điểm chưa chốt | Đã tạo |

**Code trước/sau:** Không có thay đổi mã nguồn trong phiên này. Các thay đổi chỉ là file Markdown mới.

## 5. Thảo luận và quyết định

- **Đã ghi nhận:** Sáu nguyên tắc do người dùng yêu cầu (mục 2).
- **Đề xuất cần người dùng xét:** yêu cầu phê duyệt cả các thay đổi code sau khi xem TRƯỚC/SAU; xử lý phát sinh ngoài workflow bằng workflow mới thay vì sửa workflow đã khóa; cấu trúc `notebooks/`, `src/phases/`, `workflows/`, `history/`.
- **Đã chốt:** Chưa có nội dung nào trong `RULES.md` được xem là đã chốt bằng phê duyệt cuối cùng.
- **Chưa có:** đề tài đồ án, repo thực tế, các phase cụ thể, workflow triển khai, tiêu chí kiểm thử kỹ thuật.

## 6. Kiểm chứng

- Kiểm chứng có thể làm: kiểm tra rằng `RULES.md` và file nhật ký đã được tạo trong gói dự thảo.
- **Không chạy kiểm thử code** vì chưa có mã nguồn dự án và chưa được phép triển khai phase.

## 7. Rủi ro/giới hạn và bước tiếp theo

- File hiện nằm trong gói tải về; chưa được chép vào repo thực tế hoặc hướng dẫn Project của người dùng.
- Cần người dùng rà soát, điều chỉnh và **phê duyệt rõ ràng bản Rules** trước khi coi là quy tắc cố định.
- Nếu có đề nghị sửa Rules, tạo phiên bản nháp mới có ghi khác biệt; không khẳng định đã được duyệt.
