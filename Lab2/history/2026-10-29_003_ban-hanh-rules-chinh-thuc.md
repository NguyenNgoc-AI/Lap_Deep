# LOG-003 — Ban hành PROJECT RULES v1.0 chính thức

- **Ngày:** 2026-10-29 (Asia/Ho_Chi_Minh)
- **Session ID:** 2026-10-29-003
- **Loại công việc:** Hoàn thiện tài liệu quản trị; **không có chỉnh sửa mã nguồn**.
- **Yêu cầu/phê duyệt của người dùng:** “Thêm các đề xuất của bạn vào và làm thành Rules cuối cùng”.
- **Workflow/GATE A kỹ thuật:** Không áp dụng cho hành động quản trị ban hành Rules theo chấp thuận trực tiếp của người dùng.
- **GATE B code:** Không áp dụng; không có `.py`, `.ipynb` hay config code được sửa.
- **Trạng thái:** COMPLETED — bản Rules 1.0 đã ban hành trong gói file; chưa đồng bộ vào repo đồ án.

## 1. Mục tiêu và hiện trạng trước khi làm

- Đọc `RULES.md` v1.0-draft và các log 001, 002 hiện có.
- Giữ nguyên yêu cầu nền tảng của người dùng: preview thay đổi code trước/sau trên chat, notebook main điều phối phase `.py`, workflow khóa sau duyệt, log `.md` mọi phiên, tự phản biện, cơ chế chống lệch Rules.
- Log 002 đề xuất 12 hạng mục mới; người dùng đã yêu cầu thêm toàn bộ vào Rules cuối cùng.

## 2. Các quyết định ĐÃ CHỐT

- **GATE A và GATE B là hai sự chấp thuận độc lập.**
- **Workflow LOCKED bất biến**; phát sinh tạo WF bổ sung/thay thế mới, không sửa gốc.
- **Before/After** lấy từ code file thực tế; mọi CHG phải có phạm vi, tác động, test, rollback.
- **Notebook main** điều phối module `.py` theo phase, xem source thật, debug từng phase, chống stale output.
- **Git/backup** và bảo vệ công việc chưa commit, không tự dùng thao tác phá hủy.
- **Project State**, **DoD**, **contract**, **reproducibility**, **data/security**, **traceability**, **STOP**, **log append-only** trở thành quy định chính thức.
- Các hoạt động chỉ-đọc/soạn phương án và log là ngoại lệ chuẩn bị, không được lấy làm cớ sửa code khi chưa duyệt.

## 3. Tệp thay đổi — BEFORE / AFTER

| File | BEFORE | AFTER | Trạng thái |
|---|---|---|---|
| `RULES.md` | v1.0-draft, 10 mục/tiểu mục 0–10, thiếu định nghĩa chi tiết 12 hạng mục | v1.0 FINAL, mục 0–18, hợp nhất yêu cầu gốc + 12 đề xuất | Đã thay thế nội dung tài liệu |
| `versions/RULES_v1.0-draft.md` | Không tồn tại | Bảo tồn nguyên văn bản nháp trước khi hoàn thiện | Đã tạo |
| `PROJECT_STATE.md` | Không tồn tại | Ghi Rules v1.0 có hiệu lực, không có WF/phase/code được triển khai, các vấn đề còn mở | Đã tạo |
| `history/2026-10-29_003_ban-hanh-rules-chinh-thuc.md` | Không tồn tại | Nhật ký quyết định, thay đổi, kiểm tra, trạng thái | Đã tạo |

**Code trước/sau:** Không áp dụng, **không có thay đổi mã nguồn**. Diff tài liệu được bảo tồn qua bản nháp và bản chính thức.

## 4. Cách thức và ảnh hưởng

- Soạn lại Rules để thống nhất thuật ngữ, gộp nội dung trùng, bổ sung điều khoản vận hành và checklist.
- Không thay đổi nội dung của hai nhật ký cũ.
- Không tạo notebook, module phase, file dữ liệu, workflow triển khai hay commit Git.
- Cơ chế nội bộ đưa vào Rules có hiệu lực cho công việc tiếp theo, với điều kiện tài liệu được nạp trong phiên tương ứng.

## 5. Rủi ro và các điểm PHẢN BIỆN đã xử lý

1. **Không thể bảo đảm AI luôn nhớ Rules qua mọi phiên:** cần lưu vào repo/hướng dẫn Project và đọc lại.
2. **WF bất biến có thể trở thành rào cản sửa bug:** giải pháp chặn và lập WF bổ sung, không lén thay bản khóa.
3. **OOP không phải mục tiêu tự thân:** ưu tiên module hóa/contract, dùng class khi phù hợp.
4. **In source có thể lộ secret:** xem source thực nhưng che giá trị nhạy cảm, không che logic cần duyệt.
5. **Tái sử dụng notebook output cũ dẫn đến nhận định sai:** yêu cầu version/reload/restart và đánh dấu output stale.
6. **Quy tắc ghi LOG mỗi phiên có thể bị cản bởi quyền ghi file:** phải báo trạng thái LOCAL_ONLY hoặc không thể tạo, không bịa đã lưu repo.

## 6. Kiểm chứng thực tế

- Đã đối chiếu yêu cầu gốc và danh sách P1–P12 của log 002 với mục tương ứng trong Rules v1.0.
- Đã kiểm tra file Rules/State/log được ghi thành công; kiểm tra syntax tài liệu cơ bản và tính tồn tại của bản draft (thông tin cuối cùng ghi nhận ở báo cáo/đầu ra lượt này).
- **Không chạy unit test hoặc pipeline**: chưa có mã nguồn đồ án.
- **Không xác nhận đã lưu repo**: file xuất hiện trong thư mục làm việc để tải xuống, chưa có repo người dùng.

## 7. Việc chưa chốt và bước tiếp theo

- Chưa có đề tài, workflow kỹ thuật đã duyệt, interface phase, tiêu chí test cụ thể, notebook hoặc Git repo.
- Người dùng đưa repo/đề bài; AI khảo sát đọc-only, đề xuất workflow đầu tiên và chờ GATE A; sau đó với mỗi CHG chờ GATE B.
- Cần đưa `RULES.md`, `PROJECT_STATE.md`, `history/` vào repo/hướng dẫn Project để các chat sau truy cập được.
