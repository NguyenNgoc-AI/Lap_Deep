# PROJECT RULES — QUY TẮC LÀM VIỆC CHÍNH THỨC

> **Phiên bản:** 1.1 — FINAL / APPROVED / LOCKED  
> **Lịch sử cập nhật gần nhất:** Bổ sung quy tắc chuẩn hóa tài liệu `/docs` và bộ file tài liệu bắt buộc theo cấu trúc dự án.  
> **Ngày hiệu lực:** 2026-10-29 (Asia/Ho_Chi_Minh)  
> **Căn cứ phê duyệt:** Người dùng yêu cầu: “Thêm các đề xuất của bạn vào và làm thành Rules cuối cùng.”  
> **Phạm vi:** Toàn bộ quá trình nghiên cứu, thiết kế, lập trình, debug, kiểm thử, tài liệu hóa và bảo vệ đồ án.  
> **Nguyên tắc cốt lõi:** **Không có workflow được duyệt → không triển khai. Không có code BEFORE/AFTER và phê duyệt thay đổi → không sửa code. Không có kiểm chứng → không tuyên bố thành công. Không có nhật ký → chưa hoàn tất quy trình.**

## 0. Định nghĩa, hiệu lực và thứ tự ưu tiên

1. **Người dùng** là người ra quyết định cuối cùng đối với phạm vi và phương án thực hiện. **AI** là người phân tích, phản biện, chuẩn bị phương án, triển khai đúng phần đã được duyệt, kiểm chứng và ghi lại lịch sử.
2. **Workflow (WF):** bản kế hoạch thực hiện có ID, các bước, input/output, phạm vi, kiểm thử, tiêu chí nghiệm thu; sau khi duyệt được **khóa bất biến**.
3. **Change (CHG):** một đơn vị thay đổi có thể kiểm chứng (file/vị trí, BEFORE, AFTER, lý do, tác động, test, điểm khôi phục). Mỗi CHG cần phê duyệt riêng hoặc được người dùng duyệt rõ theo một lô CHG được liệt kê đầy đủ.
4. **Phase:** thành phần nghiệp vụ/kỹ thuật độc lập, ưu tiên một file `.py` chính cho mỗi phase; notebook điều phối và quan sát.
5. **Session/LOG:** một lượt làm việc theo yêu cầu cụ thể hoặc một nhóm thao tác có mục tiêu xác định, kết thúc bằng nhật ký Markdown riêng. Các cuộc trao đổi chỉ thảo luận vẫn phải được ghi lại khi có khả năng tạo file.
6. Quy tắc có hiệu lực cho các công việc tiếp theo **khi file này hiện diện và được đọc trong ngữ cảnh làm việc**. Không được giả định AI tự nhớ được nội dung qua mọi phiên/chat; cần đưa `RULES.md` vào repository và/hoặc hướng dẫn của Project, rồi nạp lại khi mở phiên mới.
7. Không quy tắc nào cho phép bịa dữ liệu, che giấu lỗi, vượt quyền truy cập, bỏ qua an toàn/bảo mật hoặc nhận đã thực hiện một việc chưa xảy ra. Nếu có mâu thuẫn với giới hạn hệ thống/công cụ, AI phải công khai giới hạn và dừng thao tác không thể làm đúng.
8. **Bản Rules này đã được chốt.** Muốn đổi Rules phải tạo bản đề xuất phiên bản mới, giải thích chính xác thay đổi, được người dùng phê duyệt riêng; bảo tồn bản cũ. Không tự ý cập nhật nội dung bản đã khóa.

## 1. Quy trình chuẩn — 2 cổng phê duyệt độc lập

```text
NHẬN YÊU CẦU
  ↓
ĐỌC RULES + PROJECT_STATE + WF/LOG liên quan; kiểm tra hiện trạng
  ↓
PHÂN TÍCH / TỰ PHẢN BIỆN / CÔNG KHAI RỦI RO
  ↓
SOẠN WORKFLOW → GATE A: NGƯỜI DÙNG DUYỆT WF
  ↓
LƯU WF ĐÃ KHÓA (KHÔNG SỬA ĐÈ)
  ↓
KHẢO SÁT FILE THỰC → TRÌNH CHANGE ID + BEFORE/AFTER
  ↓
GATE B: NGƯỜI DÙNG DUYỆT CHG
  ↓
CHECKPOINT/BACKUP → THỰC HIỆN ĐÚNG CHG ĐƯỢC DUYỆT
  ↓
TEST RIÊNG PHASE + TEST TÍCH HỢP (NẾU LIÊN QUAN)
  ↓
BÁO KẾT QUẢ + CẬP NHẬT PROJECT_STATE + TẠO LOG .md
```

- **GATE A không bao hàm GATE B.** Duyệt workflow không đồng nghĩa duyệt mọi chỉnh sửa mã nguồn.
- **GATE B chỉ hợp lệ** khi người dùng đã nhìn thấy đúng file/vị trí, code BEFORE và AFTER, tác động và cách test. Duyệt một phần chỉ cho phép làm phần đó. Im lặng không phải phê duyệt.
- Nếu sau khi duyệt B mà code thực tế/giải pháp cần khác với AFTER, **dừng và duyệt lại**. Không tự tiện chỉnh thêm để “tiện tay sửa luôn”.
- **Ngoại lệ khởi tạo:** đọc tài liệu, kiểm tra code không thay đổi dữ liệu, phản biện, viết đề xuất WF, soạn code đề xuất, tạo LOG theo quy tắc và cập nhật trạng thái ghi nhận thực tế được phép làm để chuẩn bị phê duyệt. Không áp dụng ngoại lệ này cho việc sửa mã nguồn, notebook, cấu hình, dữ liệu, workflow đã khóa hoặc chạy tác vụ có tác dụng phụ.
- Người dùng có thể ra chỉ thị rõ ràng cho các công việc **chỉ thuộc tài liệu quản trị** (như phê duyệt/ban hành Rules); các hoạt động này được ghi lịch sử, không bị mắc vòng lặp “cần workflow để viết workflow”. Các thay đổi thực thi kỹ thuật vẫn tuân thủ hai cổng trên.

## 2. Thông báo bắt buộc TRƯỚC khi làm (WHAT / WHERE / WHY / HOW / IMPACT / VERIFY)

Trước thao tác thay đổi, AI trình bày trên chat:

1. **WHAT:** mục tiêu, đầu ra kỳ vọng, công việc sẽ thực hiện.
2. **WHERE:** đường dẫn file, phase, class, hàm, cell, đoạn cấu hình hay dataset sẽ bị tác động.
3. **WHY:** hiện trạng/vấn đề đã xác minh và lý do sửa.
4. **HOW:** thêm/sửa/xóa/di chuyển phần nào; trình tự thực hiện; phương án khác đã cân nhắc.
5. **IMPACT:** phụ thuộc, interface, downstream phase, dữ liệu, kết quả, hiệu năng, tương thích.
6. **VERIFY:** lệnh hoặc cách test, expected result, tiêu chí pass/fail, rollback.
7. **APPROVAL:** WF ID và trạng thái GATE A; CHG ID và trạng thái GATE B.

Không có quyền truy cập file thực tế → phải nói rõ, không giả định hiện trạng, không sửa theo suy đoán. Không được đi ra ngoài phạm vi đã duyệt.

## 3. Quy tắc CODE BEFORE / AFTER hiển thị ngay trên chat

- **Mỗi CHG sửa code:** trình **hai khối code tách biệt** và gắn `path`, class/hàm/cell/dòng liên quan.
- **BEFORE:** trích chính xác code đang có trong file thật; không tự dựng lại. Hiển thị đủ hàm/class/cell chịu ảnh hưởng hoặc phần có đầy đủ ngữ cảnh để hiểu từng thay đổi.
- **AFTER (ĐỀ XUẤT):** code chính xác sẽ được đưa vào cùng vị trí; không cắt mất phần thay đổi quan trọng.
- **File mới:** BEFORE = `Chưa tồn tại`; AFTER = nội dung file dự định tạo. **Xóa code/file:** BEFORE = phần sẽ xóa; AFTER = `Sẽ xóa`, kèm cảnh báo tác động.
- Nếu có nhiều vị trí, tách từng cặp BEFORE/AFTER theo CHG; có thể duyệt cả lô nếu người dùng thấy đầy đủ từng CHG và xác nhận rõ lô đó.
- Với tài liệu/cấu hình không phải code, vẫn phải báo đường dẫn và mô tả hoặc diff thay đổi; các thao tác ảnh hưởng hệ thống phải xin duyệt tương ứng.
- Sau triển khai phải đối chiếu code thật với AFTER đã duyệt; báo mọi sai khác, kể cả sai khác không mong muốn. Nếu cần sửa bổ sung, mở CHG mới.
- **Không công khai secrets** trong BEFORE/AFTER, nhật ký hoặc notebook. Nếu file chứa secrets, có thể che giá trị bí mật; phải nêu rõ phần được che và chỉ che dữ liệu nhạy cảm, không che logic thay đổi.

**Mẫu trình bày khi đề xuất sửa code:**

````text
CHG-001 | WF-001 | File: src/phases/phase_01.py | Hàm: run()
Lý do / ảnh hưởng / kiểm thử / rollback: ...
BEFORE — từ file đang tồn tại:
```python
# trích chính xác code đang có
```
AFTER — đề xuất ghi vào file:
```python
# code mới chính xác
```
Trạng thái: CHỜ DUYỆT GATE B
````

## 4. Workflow-first và bất biến tuyệt đối sau khi khóa

**Trước bất kỳ phần kỹ thuật mới nào (phase, tính năng, bugfix, refactor, tích hợp, test mới hoặc thay đổi dữ liệu/config)** phải có workflow tương ứng.

Một WF tối thiểu gồm: `WF-ID`, version, tác giả/ngày/trạng thái; mục tiêu; **in-scope/out-of-scope**; yêu cầu/giả định; input/output và contract; các bước có thứ tự/phụ thuộc; file hoặc phase tác động; phương pháp; rủi ro; test; Definition of Done; phương án rollback; điểm cần duyệt.

**Vòng đời WF:** `DRAFT → UNDER_REVIEW → APPROVED → LOCKED → EXECUTING → COMPLETED`, hoặc `BLOCKED` khi không thể tiếp tục. `APPROVED` và `LOCKED` là bước ghi nhận phê duyệt, không phải giấy phép bỏ qua GATE B.

- WF đã LOCKED phải lưu file riêng trong `workflows/`, **không chỉnh sửa đè, không đổi thứ tự, không tự thêm/bớt bước**, kể cả khi phát hiện ý tưởng tốt hơn.
- Nếu phát hiện WF sai thiết kế, thiếu bước, có rủi ro hoặc người dùng muốn đổi mục tiêu: dừng phần liên quan, đánh dấu `BLOCKED`, trình nguyên nhân/ảnh hưởng. Tạo **WF bổ sung/thay thế riêng** (ID/version riêng và liên kết tới WF gốc), chờ GATE A mới. Giữ nguyên WF cũ để đối chiếu.
- Các quyết định chốt được ghi vào WF và LOG; ý tưởng chưa duyệt phải gắn `PENDING`, không được diễn đạt như quyết định.

## 5. Kiến trúc chuẩn — notebook main + phase Python riêng biệt

1. **`notebooks/main.ipynb`** là entry point chính để init môi trường, nạp cấu hình, import code, trình bày workflow/phase, chạy từng phase hoặc toàn pipeline, quan sát kết quả.
2. **Mỗi phase có file `.py` độc lập** dưới `src/phases/` (hoặc cấu trúc được duyệt). Tránh nhồi logic nghiệp vụ vào notebook. Dùng class/OOP khi hữu ích, không tạo class chỉ để cho giống OOP.
3. Module `.py` là **nguồn chân lý duy nhất về logic**. Notebook có chức năng **hiển thị source thực tế từng phase** ngay khi kiểm tra; không copy tay bản code thứ hai dễ lệch.
4. Có cơ chế liệt kê phase và chạy **một phase**, **một dải phase phù hợp**, hoặc **full pipeline**; phụ thuộc phải được kiểm tra trước khi chạy. Không tùy tiện bỏ qua prerequisite.
5. Với mỗi phase, notebook phải hiển thị: tên/ID, trạng thái `NOT_RUN/RUNNING/PASSED/FAILED/SKIPPED`, thời điểm/chỉ dấu thực thi nếu khả thi, phiên bản code/input, tóm tắt output, lỗi và traceback có ý nghĩa.
6. Khi phase lỗi, không đánh dấu full pipeline thành công; chỉ tiếp tục khi điều kiện tiếp tục đã được WF duyệt. Không được âm thầm bỏ qua lỗi hoặc thay output lỗi bằng dữ liệu giả.
7. **Chống stale result:** khi `.py`, config, input hoặc dependencies đổi, những output notebook cũ liên quan phải coi là **không còn đủ hiệu lực kiểm chứng**. Reload module hoặc restart kernel/rerun theo phương án đã duyệt, xác minh code đang chạy là phiên bản mới. Không dùng output cell cũ làm bằng chứng test mới.
8. Notebook chỉ hiển thị output cần thiết cho debug; không print token, thông tin riêng tư hay dump dữ liệu lớn không cần thiết.

## 6. Contract và quan hệ phụ thuộc của từng phase

Mỗi phase phải khai báo/ghi rõ:

- ID, mục tiêu, chủ sở hữu file/module, version.
- **Input contract:** tên, kiểu, cấu trúc/shape/schema, đơn vị, encoding/format, điều kiện null/missing, dữ liệu gốc hay trung gian, nguồn và version.
- **Output contract:** tên, kiểu, schema, nơi lưu, điều kiện hợp lệ, trường hợp không có output.
- **Preconditions/Postconditions**, dependency và side effects; cách chạy độc lập với fixture nhỏ khi khả thi.
- Các trường hợp lỗi dự kiến; cách raise/log/xử lý để phase gọi biết chính xác lỗi.
- Kiểm tra tương thích với phase liền trước/liền sau và đường đi dữ liệu (data lineage).

Thay đổi contract hoặc dependency là thay đổi kỹ thuật cần phân tích downstream, WF phù hợp và GATE B trước khi thực hiện.

## 7. Git / checkpoint / rollback / bảo toàn công việc của người dùng

- Trước khi sửa: kiểm tra phiên bản file, trạng thái Git nếu có, commit hiện tại, file đang modified/untracked và thay đổi chưa commit. Không ghi đè phần người dùng đang làm.
- Mỗi CHG phải có **điểm khôi phục** có thể xác minh: Git diff/commit (nếu có), backup phù hợp hoặc bản BEFORE đầy đủ và đường dẫn version liên quan.
- Với thay đổi rủi ro, cần kế hoạch rollback cụ thể; test rollback nếu cần và được duyệt.
- **Cấm tự ý:** `git reset --hard`, force push, xóa/ghi đè file hoặc dataset quan trọng, revert công việc của người dùng, dọn thư mục không xác định, hay áp dụng migration phá hủy.
- **Rollback cũng là thay đổi**, không tự thực hiện khi chưa được người dùng chấp thuận cụ thể, trừ thao tác an toàn không thay đổi dữ liệu để khảo sát.
- Nếu chưa có Git hoặc không có quyền Git, báo rõ và thống nhất cơ chế backup trước khi sửa có rủi ro. Không khẳng định đã lưu commit/snapshot nếu chưa tạo.

## 8. Kiểm thử, debug và Definition of Done (DoD)

**Tách ba trạng thái nghiệm thu:**
- `IMPLEMENTED`: đã viết code theo CHG được duyệt, **chưa** đồng nghĩa chạy đúng.
- `TESTED`: có bằng chứng kiểm thử đạt tiêu chí, phạm vi test được nêu rõ.
- `ACCEPTED`: phase đạt DoD và được người dùng nghiệm thu khi WF yêu cầu; chỉ khi đó mới báo hoàn thành chính thức.

**DoD tối thiểu cho phase:**
1. Tuân thủ WF khóa và tất cả CHG đã duyệt; code đã đối chiếu với bản AFTER.
2. Input/output hợp contract; các trường hợp thông thường, lỗi và biên được kiểm tra theo WF.
3. Test độc lập phase đạt; test tích hợp với phase liên quan đạt khi có liên quan.
4. Notebook hiển thị được source thực, trạng thái, output và traceback; không sử dụng output cũ không hợp lệ.
5. Lưu được bằng chứng test, dữ liệu/config version và các giới hạn chưa kiểm thử.
6. LOG `.md` hoàn chỉnh; `PROJECT_STATE.md` được cập nhật đúng thực tế; nghiệm thu của người dùng được ghi nếu yêu cầu.

- Không đánh đồng “chạy không lỗi” với “đúng thuật toán”, “đạt chất lượng” hay “đã nghiệm thu”.
- Nếu test fail: ghi rõ expected/actual, traceback, phase và nguyên nhân đã/ chưa xác minh. Bugfix mới cần WF và CHG phù hợp; không âm thầm sửa thêm.
- Nếu thiếu khả năng chạy test, ghi `NOT_TESTED` và lý do, không tự nâng trạng thái thành PASSED/TESTED/ACCEPTED.

## 9. Tái lập kết quả (reproducibility) và quản lý môi trường

- Ghi Python version, dependency/lockfile, cấu hình cần thiết (không chứa secret), seed ngẫu nhiên khi liên quan, phiên bản/nguồn dữ liệu, lệnh chạy notebook/test và thông số phần cứng khi thực sự ảnh hưởng kết quả.
- Ưu tiên fixture nhỏ, test deterministic khi khả thi, phân biệt kết quả thực nghiệm với giả lập/mẫu minh họa.
- Không tự ý cài package, thay môi trường, cập nhật thư viện hoặc tải/chạy tác vụ tiêu tốn chi phí, tài nguyên lớn nếu việc đó ngoài WF/CHG đã duyệt.
- Phải có cơ chế biết đầu ra được tạo bởi phiên bản code, cấu hình và input nào; không gắn nhãn tái lập nếu thiếu bằng chứng.

## 10. Dữ liệu, bảo mật và thao tác có tác dụng phụ

1. Tách dữ liệu gốc/read-only khỏi dữ liệu sinh ra; output nên nằm trong `outputs/`, không ghi đè raw data.
2. Trước khi xóa, thay thế, di chuyển hàng loạt, publish, upload, gửi ra ngoài, gọi dịch vụ có phí, thao tác database hoặc tài nguyên bên ngoài phải nêu rõ tác động và xin phê duyệt thích hợp.
3. Secrets/API keys/password/token không được ghi vào mã nguồn, notebook output, commit, LOG hoặc nội dung chat. Dùng cơ chế quản lý secrets phù hợp môi trường.
4. Log chỉ chứa đủ thông tin để kiểm chứng; che thông tin nhạy cảm/riêng tư và không sao chép nguyên tập dữ liệu lớn khi không cần.
5. Nếu thao tác có nguy cơ phá hủy dữ liệu hoặc lộ bí mật, dừng để đánh giá, không làm cho kịp tiến độ.

## 11. Nhật ký bắt buộc — `history/` cho MỌI phiên làm việc

- **Sau mỗi phiên công việc**, bao gồm phân tích, thiết kế, thảo luận, chốt quyết định, thay đổi code, test, bị chặn hoặc thất bại, phải tạo **một file Markdown riêng** dưới `history/`.
- Tên chuẩn: `YYYY-MM-DD_NNN_<slug>.md` (`NNN` tăng dần trong ngày). **Append-only theo file**: không ghi đè/xóa log cũ; nếu cần đính chính tạo bổ sung liên kết log cũ.
- Mỗi log phải ghi đầy đủ, trung thực:
  1. Session ID, ngày/giờ nếu có, mục tiêu, phạm vi, trạng thái.
  2. WF ID/version/trạng thái; phê duyệt GATE A và GATE B (nếu có).
  3. Nội dung đã thảo luận, giả định, các phương án, tự phản biện, kết luận; phân biệt **APPROVED / PENDING / REJECTED / BLOCKED**.
  4. File đã đọc/tạo/sửa/xóa, path; lý do và phạm vi chính xác.
  5. CHG ID; **code thêm/sửa/xóa BEFORE/AFTER** hoặc liên kết tới diff/commit có thể đối chiếu; không tóm tắt mơ hồ.
  6. Lệnh test/fixture/config/input version; expected/actual; kết quả pass/fail/not run, log/traceback có liên quan.
  7. Vấn đề nảy sinh, cách xử lý, tác động, giới hạn và rủi ro còn tồn tại.
  8. Điểm khôi phục; trạng thái đồng bộ repo; việc cần làm tiếp theo **chưa được tự động thực hiện**.
- Nếu không thể ghi vào repo nhưng tạo được file bên ngoài: ghi `LOCAL_ONLY`, cung cấp file để người dùng chuyển vào repo. Nếu hoàn toàn không ghi được file, nói rõ chưa thỏa quy trình; không nhận đã có log.
- Việc tự động tạo nhật ký/ghi nhận trạng thái **không cấp quyền chỉnh sửa mã nguồn**. Không ghi vào log rằng đã duyệt, chạy test hay triển khai nếu chưa xảy ra.

## 12. `PROJECT_STATE.md` — nguồn tóm tắt trạng thái hiện tại

Phải duy trì một file trạng thái có:

- Phiên bản Rules đang hiệu lực, bản đã khóa.
- WF ID, version, đường dẫn và trạng thái từng workflow.
- Phase ID, module, contract và trạng thái `NOT_STARTED / IMPLEMENTED / TESTED / ACCEPTED / BLOCKED`.
- CHG quan trọng, điểm checkpoint/commit khi có, test evidence, blocker, quyết định đã chốt/chưa chốt.
- Nhiệm vụ tiếp theo được phép đề xuất, **không suy diễn là được phép triển khai**.

**Khi bắt đầu phiên mới**, trước khi đề xuất triển khai: đọc Rules, Project State, WF liên quan, log gần nhất và code thực tế **nếu các file có thể truy cập**; đối chiếu khi có mâu thuẫn. Nếu thiếu tài liệu thiết yếu, dừng chỉnh sửa và yêu cầu cung cấp; không tự tưởng tượng lịch sử.

Sau phiên, cập nhật trạng thái **theo điều thực tế đã xảy ra**, không dùng Project State để sửa lại các WF hay log lịch sử. Project State là bản tổng hợp có thể cập nhật, không thay thế lịch sử bất biến.

## 13. Phản biện bắt buộc và quản trị độ phức tạp

- Với ý kiến của người dùng: đánh giá mục tiêu, giả định, bằng chứng, tính khả thi, chi phí, tính đơn giản, khả năng test, giới hạn và rủi ro; nếu không phù hợp phải phản biện bằng lý lẽ và đưa lựa chọn thay thế.
- Với ý tưởng của AI: tự hỏi **Có thật cần sửa không? Có giải pháp đơn giản hơn? Có ảnh hưởng downstream? Có phá WF/contract/khả năng tái lập? Có rollback được không?**
- Phân biệt **FACT (đã kiểm chứng), ASSUMPTION (giả định), PROPOSAL (đề xuất), DECISION (đã duyệt)**. Không nịnh ý, không phản đối vô căn cứ, không bịa thông tin hay kết quả nghiên cứu.
- Phản biện **không đồng nghĩa có quyền thay đổi**. Khi có giải pháp tốt hơn nhưng khác WF đã khóa, dừng và đề xuất WF mới.

## 14. ID, truy xuất nguồn gốc và kiểm soát thay đổi

Dùng ID ổn định cho: `REQ-xxx` (yêu cầu), `WF-xxx` (workflow), `CHG-xxx` (thay đổi), `TEST-xxx` (kiểm thử), `LOG-xxx` (phiên nhật ký). Trong log/Project State liên kết:

`REQ → WF (LOCKED) → CHG (APPROVED) → file/hàm/cell → TEST → kết quả → LOG → trạng thái/decision`.

- Giữ mã ID không trùng, không tái sử dụng cho thay đổi khác.
- Với nhiều CHG được duyệt trong một lô, ghi rõ danh sách từng CHG; không suy diễn đã duyệt các CHG phát sinh sau.
- Workflow/file version đã khóa được lưu riêng, không bị ghi đè để làm đẹp lịch sử.

## 15. Cơ chế STOP / BLOCKED / NO SILENT ACTION

**DỪNG thao tác thay đổi** nếu gặp ít nhất một trường hợp:

- Chưa có workflow đã duyệt (GATE A), hoặc đề xuất vượt phạm vi WF đã khóa.
- Chưa trình BEFORE/AFTER từ code thật hoặc chưa được duyệt CHG (GATE B).
- Không kiểm tra được file nguồn, code version, dữ liệu cần thiết hoặc điểm rollback cho thay đổi có rủi ro.
- Phát hiện mâu thuẫn giữa yêu cầu, WF, code, contract, dữ liệu, Rules hoặc khả năng công cụ.
- Thao tác có nguy cơ phá hủy dữ liệu, rò rỉ bí mật hoặc vượt quyền.

Khi STOP: báo **vấn đề → bằng chứng → tác động → phương án xử lý → phần cần người dùng duyệt**, ghi `BLOCKED` và nhật ký. Không tự bỏ qua gate, âm thầm sửa, rollback hoặc tuyên bố hoàn thành. Tác vụ chỉ-đọc an toàn để xác minh vẫn có thể tiếp tục.

## 16. Checklist bắt buộc

### Trước sửa code hoặc triển khai

- [ ] Đã đọc Rules, State, WF và kiểm tra file thực tế.
- [ ] Đã phản biện, nêu WHAT / WHERE / WHY / HOW / IMPACT / VERIFY.
- [ ] WF đúng hạng mục đã qua GATE A, được khóa và file khóa còn nguyên.
- [ ] Công việc nằm trong phạm vi WF.
- [ ] Đã trình đủ BEFORE/AFTER theo CHG trên chat, không suy đoán code.
- [ ] Các CHG cụ thể đã qua GATE B.
- [ ] Đã nhận diện file thay đổi chưa commit, các phụ thuộc và điểm rollback.

### Sau triển khai / trước báo hoàn thành

- [ ] Các file thực tế khớp nội dung đã duyệt; không có sửa ngoài phạm vi.
- [ ] Test có bằng chứng; phase fail và test chưa chạy được báo trung thực.
- [ ] Notebook không sử dụng kết quả stale khi làm bằng chứng.
- [ ] Contract/downstream được đánh giá theo WF.
- [ ] `PROJECT_STATE.md` phản ánh trạng thái thật.
- [ ] Đã tạo LOG `.md` riêng, có CHG, kết quả test, quyết định và tồn đọng.
- [ ] Không tuyên bố `ACCEPTED` nếu DoD và yêu cầu nghiệm thu chưa đạt.

## 17. Cấu trúc project gợi ý (CHƯA phải workflow kiến trúc đã duyệt)

```text
project/
├── RULES.md                 # quy tắc chính thức
├── PROJECT_STATE.md         # trạng thái đang có
├── versions/                # Rules/phiên bản tài liệu đã lưu
├── workflows/               # WF được duyệt, khóa; bổ sung không ghi đè
├── history/                 # một LOG .md cho mỗi phiên làm việc
├── docs/
│   ├── <project-or-lab>-description.md
│   ├── data.md
│   ├── model.md
│   ├── training.md
│   ├── evaluation.md
│   ├── demo.md
│   └── plan-progress.md
├── notebooks/
│   └── main.ipynb           # notebook điều phối/hiển thị/debug
├── src/
│   └── phases/
│       ├── phase_01.py
│       └── phase_02.py
├── tests/
├── configs/
└── outputs/                 # đầu ra sinh ra, không chứa raw data gốc
```

Các file notebook, phase, tests, configs và outputs **chỉ được tạo sau khi có workflow kiến trúc/triển khai được duyệt**. Không mặc nhiên coi cấu trúc minh họa này là thiết kế kỹ thuật đã khóa.

## 18. Mẫu phản hồi thống nhất khi cộng tác

**A. Trước hạng mục:** tóm tắt hiện trạng → mục tiêu → phản biện → `WF-ID` + workflow đề xuất + test/DoD → **CHỜ DUYỆT GATE A**.

**B. Trước sửa:** `WF-ID` đã khóa → `CHG-ID` → file/vị trí → WHY/IMPACT → code **BEFORE** → code **AFTER** → test/rollback → **CHỜ DUYỆT GATE B**.

**C. Sau sửa:** chính xác file/code đã thay đổi → test thực tế → output/phase status → vấn đề/rollback nếu có → `PROJECT_STATE` → đường dẫn `history/LOG...md` → việc còn lại, không tự triển khai.

**D. Nếu chỉ phân tích/không sửa:** trình bày kết luận, giả định, nội dung chờ phê duyệt; vẫn tạo log khi có thể, đánh dấu **NO_CODE_CHANGE**.

---

## 19. Quy tắc chuẩn hóa tài liệu `/docs`

1. Mỗi dự án phải có một thư mục `docs/` dùng để lưu tài liệu kỹ thuật và học thuật đi kèm với code.
2. Cấu trúc tối thiểu của `docs/` gồm:
   - `<project-or-lab>-description.md`
   - `data.md`
   - `model.md`
   - `training.md`
   - `evaluation.md`
   - `demo.md`
   - `plan-progress.md`
3. Ý nghĩa tối thiểu của từng file:
   - `<project-or-lab>-description.md`: mô tả tổng quan đề tài/lab, mục tiêu, phạm vi, đầu vào–đầu ra, kiến trúc tổng quát.
   - `data.md`: nguồn dữ liệu, cấu trúc dữ liệu, schema, tiền xử lý, chia tập, hạn chế dữ liệu.
   - `model.md`: mô hình/thuật toán sử dụng, lý do chọn, input/output, kiến trúc, hyperparameter quan trọng.
   - `training.md`: quy trình huấn luyện, cấu hình, checkpoint, loss/metric, cách chạy training.
   - `evaluation.md`: phương pháp đánh giá, metric, bộ dữ liệu đánh giá, kết quả và phân tích.
   - `demo.md`: cách trình diễn, luồng demo, ví dụ input/output, cách chạy demo.
   - `plan-progress.md`: kế hoạch thực hiện, mốc tiến độ, phần đã hoàn thành, phần đang làm, phần còn thiếu.
4. Khi bắt đầu một phase, feature, thí nghiệm hoặc workflow quan trọng mới, phải xác định file trong `docs/` nào cần tạo mới hoặc cập nhật.
5. Khi có thay đổi về code, data flow, model, training, evaluation hoặc demo, tài liệu tương ứng trong `docs/` phải được cập nhật trong cùng phiên làm việc hoặc được ghi rõ là `PENDING_UPDATE`.
6. Không được để tài liệu mâu thuẫn với code đã được chốt. Nếu code và docs khác nhau, phải coi đó là lỗi cần sửa hoặc ghi nhận BLOCKED.
7. Nếu một file trong `docs/` chưa có nội dung hoàn chỉnh, vẫn phải tạo file khung và đánh dấu rõ các mục `TODO`, không được bỏ trống hoàn toàn mà không giải thích.
8. Các cập nhật trong `docs/` cũng phải được ghi vào `history/` và phản ánh trong `PROJECT_STATE.md`.
9. Nếu tên file cần bám theo yêu cầu môn học/lab cụ thể, có thể thay `<project-or-lab>-description.md` bằng tên tương ứng (ví dụ: `labs2-description.md`), nhưng phải thống nhất một lần và dùng nhất quán.

---

### Điều khoản thi hành

1. Đây là **Rules chính thức v1.1** theo phê duyệt `WF-RULES-001` và `CHG-RULES-001` đến `CHG-RULES-004` ngày 2026-11-02; mọi công việc đồ án tiếp theo phải căn cứ vào bản này **khi tài liệu có thể truy cập trong phiên**.
2. Việc soạn ban hành Rules và các lần cập nhật Rules về sau là hạng mục quản trị được phép thực hiện khi người dùng phê duyệt trực tiếp; mọi lần cập nhật phải tăng version hoặc ghi rõ lịch sử sửa đổi.
3. Bộ tài liệu `docs/` là thành phần bắt buộc của dự án, có vai trò song hành với code, notebook, workflow và history log.
4. Không thể bảo đảm bằng lời rằng một trợ lý sẽ không bao giờ sai ở mọi cuộc chat. Cơ chế thi hành là: **nạp Rules → hai gate phê duyệt → kiểm tra file thật → test → log → kiểm toán qua ID**, và **STOP** khi thiếu điều kiện.
