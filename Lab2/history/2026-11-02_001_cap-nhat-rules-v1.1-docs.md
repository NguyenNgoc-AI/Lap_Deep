# LOG — Ban hành Rules v1.1 và chuẩn hóa `/docs`

- **Session:** LOG-20261102-001
- **Ngày:** 2026-11-02 (Asia/Ho_Chi_Minh)
- **Trạng thái:** COMPLETED — DOCUMENTATION_ONLY / NO_SOURCE_CODE_CHANGE
- **Workflow:** `WF-RULES-001` — GATE A: APPROVED, LOCKED
- **Gate B:** `CHG-RULES-001` đến `CHG-RULES-004` — APPROVED
- **Bằng chứng phê duyệt:** Người dùng xác nhận: “Duyệt WF-RULES-001. Duyệt CHG-RULES-001 đến CHG-RULES-004. Dùng `plan-progress.md`.”

## Mục tiêu và quyết định

- Bổ sung chuẩn `docs/` theo cây thư mục người dùng cung cấp.
- Giữ đúng 7 tên tài liệu Markdown đã duyệt. Chọn **`plan-progress.md`**, không phải `.sta`.
- Workflow được phê duyệt và khóa; chỉ cập nhật các tài liệu quản trị, không chạm code đồ án.

## Phản biện, giải pháp, rủi ro

- Đồng bộ tài liệu với mã nguồn giúp kiểm tra, bảo vệ đồ án và tránh tài liệu sai phiên bản.
- Sử dụng `.md` giúp các tài liệu cùng định dạng, đọc được trong repository.
- Rủi ro: `docs/` mới chỉ tồn tại dưới dạng quy tắc và mẫu cấu trúc; chưa có repo đồ án để sinh file, không được báo sai là đã sinh.
- Giới hạn: tên `<project-or-lab>-description.md` chỉ là placeholder; cần chốt khi có đề tài/lab cụ thể.

## Danh sách file thay đổi

| File | Loại | Nội dung |
|---|---|---|
| `RULES.md` | Sửa | CHG-RULES-001 đến 004 |
| `PROJECT_STATE.md` | Sửa | Chuyển phiên bản hiệu lực sang v1.1; theo dõi trạng thái |
| `versions/RULES_v1.0_FINAL_2026-10-29.md` | Tạo | Bản v1.0 nguyên gốc, không sửa |
| `workflows/WF-RULES-001.md` | Tạo | Workflow đã chốt và giới hạn phạm vi |
| `history/2026-11-02_001_cap-nhat-rules-v1.1-docs.md` | Tạo | Nhật ký này |

## BEFORE / AFTER — bản diff thực tế của RULES.md

```diff
--- RULES.md v1.0
+++ RULES.md v1.1
@@ -1,6 +1,7 @@
 # PROJECT RULES — QUY TẮC LÀM VIỆC CHÍNH THỨC
 
-> **Phiên bản:** 1.0 — FINAL / APPROVED / LOCKED  
+> **Phiên bản:** 1.1 — FINAL / APPROVED / LOCKED  
+> **Lịch sử cập nhật gần nhất:** Bổ sung quy tắc chuẩn hóa tài liệu `/docs` và bộ file tài liệu bắt buộc theo cấu trúc dự án.  
 > **Ngày hiệu lực:** 2026-10-29 (Asia/Ho_Chi_Minh)  
 > **Căn cứ phê duyệt:** Người dùng yêu cầu: “Thêm các đề xuất của bạn vào và làm thành Rules cuối cùng.”  
 > **Phạm vi:** Toàn bộ quá trình nghiên cứu, thiết kế, lập trình, debug, kiểm thử, tài liệu hóa và bảo vệ đồ án.  
@@ -257,6 +258,14 @@
 ├── versions/                # Rules/phiên bản tài liệu đã lưu
 ├── workflows/               # WF được duyệt, khóa; bổ sung không ghi đè
 ├── history/                 # một LOG .md cho mỗi phiên làm việc
+├── docs/
+│   ├── <project-or-lab>-description.md
+│   ├── data.md
+│   ├── model.md
+│   ├── training.md
+│   ├── evaluation.md
+│   ├── demo.md
+│   └── plan-progress.md
 ├── notebooks/
 │   └── main.ipynb           # notebook điều phối/hiển thị/debug
 ├── src/
@@ -282,8 +291,37 @@
 
 ---
 
+## 19. Quy tắc chuẩn hóa tài liệu `/docs`
+
+1. Mỗi dự án phải có một thư mục `docs/` dùng để lưu tài liệu kỹ thuật và học thuật đi kèm với code.
+2. Cấu trúc tối thiểu của `docs/` gồm:
+   - `<project-or-lab>-description.md`
+   - `data.md`
+   - `model.md`
+   - `training.md`
+   - `evaluation.md`
+   - `demo.md`
+   - `plan-progress.md`
+3. Ý nghĩa tối thiểu của từng file:
+   - `<project-or-lab>-description.md`: mô tả tổng quan đề tài/lab, mục tiêu, phạm vi, đầu vào–đầu ra, kiến trúc tổng quát.
+   - `data.md`: nguồn dữ liệu, cấu trúc dữ liệu, schema, tiền xử lý, chia tập, hạn chế dữ liệu.
+   - `model.md`: mô hình/thuật toán sử dụng, lý do chọn, input/output, kiến trúc, hyperparameter quan trọng.
+   - `training.md`: quy trình huấn luyện, cấu hình, checkpoint, loss/metric, cách chạy training.
+   - `evaluation.md`: phương pháp đánh giá, metric, bộ dữ liệu đánh giá, kết quả và phân tích.
+   - `demo.md`: cách trình diễn, luồng demo, ví dụ input/output, cách chạy demo.
+   - `plan-progress.md`: kế hoạch thực hiện, mốc tiến độ, phần đã hoàn thành, phần đang làm, phần còn thiếu.
+4. Khi bắt đầu một phase, feature, thí nghiệm hoặc workflow quan trọng mới, phải xác định file trong `docs/` nào cần tạo mới hoặc cập nhật.
+5. Khi có thay đổi về code, data flow, model, training, evaluation hoặc demo, tài liệu tương ứng trong `docs/` phải được cập nhật trong cùng phiên làm việc hoặc được ghi rõ là `PENDING_UPDATE`.
+6. Không được để tài liệu mâu thuẫn với code đã được chốt. Nếu code và docs khác nhau, phải coi đó là lỗi cần sửa hoặc ghi nhận BLOCKED.
+7. Nếu một file trong `docs/` chưa có nội dung hoàn chỉnh, vẫn phải tạo file khung và đánh dấu rõ các mục `TODO`, không được bỏ trống hoàn toàn mà không giải thích.
+8. Các cập nhật trong `docs/` cũng phải được ghi vào `history/` và phản ánh trong `PROJECT_STATE.md`.
+9. Nếu tên file cần bám theo yêu cầu môn học/lab cụ thể, có thể thay `<project-or-lab>-description.md` bằng tên tương ứng (ví dụ: `labs2-description.md`), nhưng phải thống nhất một lần và dùng nhất quán.
+
+---
+
 ### Điều khoản thi hành
 
-1. Đây là **Rules chính thức v1.0** theo yêu cầu chốt của người dùng ngày 2026-10-29; mọi công việc đồ án tiếp theo phải căn cứ vào bản này **khi tài liệu có thể truy cập trong phiên**.
-2. Việc soạn ban hành Rules lần này là hạng mục quản trị được người dùng phê duyệt trực tiếp; **không có mã nguồn đồ án, notebook hoặc WF kỹ thuật nào đã được phê duyệt/đụng tới** chỉ nhờ hành động ban hành Rules.
-3. Không thể bảo đảm bằng lời rằng một trợ lý sẽ không bao giờ sai ở mọi cuộc chat. Cơ chế thi hành là: **nạp Rules → hai gate phê duyệt → kiểm tra file thật → test → log → kiểm toán qua ID**, và **STOP** khi thiếu điều kiện.
+1. Đây là **Rules chính thức v1.1** theo phê duyệt `WF-RULES-001` và `CHG-RULES-001` đến `CHG-RULES-004` ngày 2026-11-02; mọi công việc đồ án tiếp theo phải căn cứ vào bản này **khi tài liệu có thể truy cập trong phiên**.
+2. Việc soạn ban hành Rules và các lần cập nhật Rules về sau là hạng mục quản trị được phép thực hiện khi người dùng phê duyệt trực tiếp; mọi lần cập nhật phải tăng version hoặc ghi rõ lịch sử sửa đổi.
+3. Bộ tài liệu `docs/` là thành phần bắt buộc của dự án, có vai trò song hành với code, notebook, workflow và history log.
+4. Không thể bảo đảm bằng lời rằng một trợ lý sẽ không bao giờ sai ở mọi cuộc chat. Cơ chế thi hành là: **nạp Rules → hai gate phê duyệt → kiểm tra file thật → test → log → kiểm toán qua ID**, và **STOP** khi thiếu điều kiện.
```

## BEFORE / AFTER — bản diff thực tế của PROJECT_STATE.md

```diff
--- PROJECT_STATE.md previous
+++ PROJECT_STATE.md new
@@ -1,43 +1,49 @@
 # PROJECT STATE — trạng thái hiện tại
 
-> **Cập nhật:** 2026-10-29 (Asia/Ho_Chi_Minh)  
-> **Nguồn tham chiếu:** `RULES.md` v1.0 FINAL / APPROVED / LOCKED  
+> **Cập nhật:** 2026-11-02 (Asia/Ho_Chi_Minh)  
+> **Nguồn tham chiếu:** `RULES.md` v1.1 FINAL / APPROVED / LOCKED  
 > **Phạm vi trạng thái:** Bộ tài liệu quản trị Rules, **không phải trạng thái repository code đồ án**.
 
 ## 1. Rules
 
-- Phiên bản có hiệu lực: **1.0 — FINAL / APPROVED / LOCKED**.
-- Lý do ban hành: Người dùng đã yêu cầu kết hợp các đề xuất và làm Rules cuối cùng.
-- Bản dự thảo được bảo tồn: `versions/RULES_v1.0-draft.md`.
-- Muốn đổi Rules: tạo đề xuất phiên bản mới, người dùng phê duyệt, lưu bản cũ; không sửa đè bản khóa.
+- Phiên bản có hiệu lực: **1.1 — FINAL / APPROVED / LOCKED**.
+- Căn cứ phê duyệt: Người dùng duyệt **WF-RULES-001** và **CHG-RULES-001 đến CHG-RULES-004**, chọn `plan-progress.md` ngày 2026-11-02.
+- Nội dung bổ sung: Quy tắc **`docs/`** tại Mục 19; 7 file tài liệu tiêu chuẩn; trách nhiệm cập nhật tài liệu song hành với code/phase.
+- Bản v1.0 chính thức được bảo tồn: `versions/RULES_v1.0_FINAL_2026-10-29.md`.
+- Bản v1.0-draft từng được đề cập trong lịch sử, nhưng chưa có file lưu trong thư mục dự án hiện truy cập được; không khẳng định tồn tại.
+- Muốn đổi Rules: tạo phiên bản mới, nêu BEFORE/AFTER và phê duyệt cụ thể; giữ nguyên các bản đã khóa.
 
 ## 2. Workflow và phase
 
 | ID | Hạng mục | Trạng thái | Nguồn |
 |---|---|---|---|
-| — | Workflow triển khai kỹ thuật | NOT_STARTED | Chưa có workflow nào được duyệt |
+| WF-RULES-001 | Chuẩn hóa Rules và `/docs` | APPROVED / LOCKED / COMPLETED | `workflows/WF-RULES-001.md` |
+| — | Workflow triển khai kỹ thuật | NOT_STARTED | Chưa có workflow triển khai đồ án được duyệt |
 | — | Notebook main | NOT_STARTED | Chưa được tạo |
 | — | Module phase Python | NOT_STARTED | Chưa được tạo |
+| — | Bộ tài liệu `docs/` thực tế | NOT_STARTED | Chỉ mới thông qua **quy tắc**, chưa khởi tạo trong repo đồ án |
 
 ## 3. Change, kiểm thử và code
 
-- CHANGE ID đã duyệt cho mã nguồn: **Chưa có**.
-- Repo/commit mã nguồn hiện tại: **Chưa được cung cấp**.
+- CHG đã duyệt cho **tài liệu quản trị**: CHG-RULES-001, CHG-RULES-002, CHG-RULES-003, CHG-RULES-004 — **ĐÃ THỰC HIỆN**.
+- CHG đã duyệt cho **mã nguồn**: Chưa có.
+- Repo/commit mã nguồn thực tế: Chưa được cung cấp.
 - Mã nguồn/Notebook đã sửa trong các phiên Rules: **Không có**.
-- Test kỹ thuật đã chạy: **Không có** (chưa có phần triển khai).
-- Nhật ký công việc: `history/2026-10-29_001_khoi-tao-project-rules.md`, `history/2026-10-29_002_kiem-tra-bo-sung-rules.md`, `history/2026-10-29_003_ban-hanh-rules-chinh-thuc.md`.
+- Kiểm tra tài liệu: thay đổi phiên bản, tồn tại mục Rule 19, bảy tên file `docs/`, tính nguyên vẹn backup và bản ZIP (xem LOG mới nhất).
+- Test kỹ thuật đã chạy: **Không có** (chưa triển khai code).
+- Nhật ký: `history/2026-10-29_001_khoi-tao-project-rules.md`, `history/2026-10-29_002_kiem-tra-bo-sung-rules.md`, `history/2026-10-29_003_ban-hanh-rules-chinh-thuc.md`, `history/2026-11-02_001_cap-nhat-rules-v1.1-docs.md`.
 
 ## 4. Quyết định đã chốt và các việc còn mở
 
-**APPROVED:** Các yêu cầu gốc của người dùng và 12 đề xuất bổ sung đã được đưa vào `RULES.md` v1.0.
+**APPROVED:** Bộ Rules v1.1, workflow WF-RULES-001 và CHG-RULES-001..004; dùng `plan-progress.md`; bắt buộc chuẩn `docs/` cho dự án khi triển khai.
 
-**PENDING:** Đề tài đồ án; repo thực tế; workflow kiến trúc notebook/phase; các input/output contract; tiêu chí nghiệm thu kỹ thuật; lựa chọn môi trường và quản lý Git cụ thể.
+**PENDING:** Đề tài đồ án; đường dẫn repo thực tế; tên cụ thể của `<project-or-lab>-description.md`; workflow kiến trúc notebook/phase; khởi tạo bộ file `docs/` trong repo; input/output contracts; tiêu chí nghiệm thu kỹ thuật; môi trường/Git.
 
 ## 5. Bắt đầu phiên tiếp theo
 
-1. Đọc `RULES.md` + `PROJECT_STATE.md` + workflow/log liên quan và mã nguồn thực tế (khi được cung cấp).
-2. Đề xuất workflow cho hạng mục kỹ thuật đầu tiên, chờ **GATE A**.
-3. Nếu cần sửa code, trình BEFORE/AFTER và chờ **GATE B**.
-4. Sau mỗi phiên tạo log và cập nhật State trung thực.
+1. Đọc Rules v1.1, Project State, workflow/log liên quan và mã nguồn thực tế (khi có).
+2. Đề xuất workflow khởi tạo cấu trúc dự án, gồm `docs/`, notebook main và các phase phù hợp; chờ **GATE A**.
+3. Với code và file kỹ thuật thực tế, trình nội dung BEFORE/AFTER rồi chờ **GATE B**.
+4. Sau mỗi phiên ghi nhật ký và trạng thái trung thực.
 
-> **Lưu ý:** Các file này đang là bản xuất từ phiên làm việc hiện tại. Chưa có bằng chứng đã đặt vào repo hoặc hướng dẫn Project của người dùng.
+> **Giới hạn:** Các file này là bản xuất quản trị. Chưa có bằng chứng chúng đã được đặt vào repository hoặc hướng dẫn Project của người dùng.
```

## Kiểm chứng và rollback

- Kiểm tra tài liệu (không phải test code): version v1.1, Rule 19, tên file, điều khoản thi hành, nguồn backup.
- SHA256 v1.0 trước sửa: `e82b51c3545b2df492324bc478afaa08cdeb1216b7539c7b983c05d7ee4a7360`
- SHA256 backup v1.0: `e82b51c3545b2df492324bc478afaa08cdeb1216b7539c7b983c05d7ee4a7360`
- SHA256 Rules v1.1: `0d8acbb8a093514552314a85f735cdcc988a2221a9d0f5fb184e9411234cc3fb`
- Rollback khả thi bằng bản v1.0 trong `versions/`, nhưng cần người dùng duyệt trước khi làm; log không bị xóa.
- Kết quả test notebook / phase Python: **NOT_RUN**, không có mã nguồn và repo đồ án.

## Phần còn lại — không tự triển khai

- Khởi tạo thư mục `docs/` trong repo đồ án, cùng các file khung: **PENDING** workflow kiến trúc cụ thể.
- Chưa chọn tên chính thức cho `<project-or-lab>-description.md`.
- Cập nhật Rules vào repository hoặc hướng dẫn Project: **LOCAL_ONLY** — chưa xác nhận đã đồng bộ.
