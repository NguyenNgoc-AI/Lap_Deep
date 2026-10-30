# LOG-008 — Triển khai và kiểm chứng CHG-002

- Ngày: 2026-10-30 (Asia/Saigon). WF-001 v1.0 LOCKED; CHG-002.
- Người dùng trả lời “ok” cho BEFORE/AFTER CHG-002: GATE B APPROVED. GATE A đã duyệt.
- Kết quả: CHG-002 IMPLEMENTED / TESTED; PHASE-01 TESTED. WF-001 đạt kiểm chứng, chờ người dùng nghiệm thu để ghi ACCEPTED. Chưa huấn luyện dataset thật.

## Hiện trạng, checkpoint và thay đổi

- Đọc PROJECT_STATE, hồ sơ WF/CHG; ba file kỹ thuật và outputs/environment/main.executed.ipynb chưa tồn tại trước khi ghi.
- WF LOCKED giữ SHA256 9DD04E4675CE28410D83400A050447157D6D90D29C7353E0A7AE85C121E31AC8.
- CHG-002 proposal SHA256 D295802D1422B2553DFD251C2BA4AC6F8D4881E5D0375093E368A0A813D291CD.
- BEFORE ba file = Chưa tồn tại. AFTER = toàn bộ code/JSON trong [CHG-002](../workflows/CHG-002_PROPOSED_phase-notebook-tests.md) đã hiển thị trên chat và được duyệt; trích xuất trực tiếp, không viết lại theo trí nhớ.
- Tạo và đối chiếu byte/content:
  - src/phases/phase_01_environment.py: dd6dfbd4f1ab2bd8d992f354ba7327a86bce567770cd277dc9f053ef9f0a79e6.
  - tests/test_environment.py: 59069eaadfb1e369b8237b5dadb6a3fa31ddbce604fbeac820a3770709c35336.
  - notebooks/main.ipynb: b061998d4134e2112d390e90af56809b1cfa16928067246106cca9e8603a3d06.
- Kernel lab2 được tạo trong D:\Lab2\.venv\share\jupyter\kernels\lab2; argv trỏ D:\Lab2\.venv\Scripts\python.exe.
- Không sửa requirements, driver, WF LOCKED, log cũ hoặc nội dung kỹ thuật ngoài AFTER. Không Git/commit; không rollback.
- Có tạo bytecode/cache/runtime phục vụ Python/Jupyter và các output được duyệt.

## Lệnh và kết quả

Tại D:\Lab2, chạy đúng ba lệnh trong CHG-002:

1. .venv\Scripts\python.exe -m unittest discover -s tests -v
   - Lần sandbox: 5 ERROR do WinError 5 khi tạo/xóa thư mục tempfile trong sandbox, không phải assertion logic.
   - Chạy lại đúng lệnh ngoài sandbox: 5/5 PASS, 1.717 giây, exit 0.
   - Bao phủ: invalid batch; XPU unavailable; OOM retry cả CPU/XPU batch4; OOM batch4 dừng; runtime error giữ traceback và FAILED.
   - Những test điều khiển dùng mock, không làm bằng chứng GPU thật.
2. .venv\Scripts\python.exe -m ipykernel install --prefix D:\Lab2\.venv --name lab2 --display-name "Lab2 (.venv)"
   - Sandbox lỗi thư mục tạm WinError5; chạy lại ngoài sandbox thành công exit0.
3. .venv\Scripts\python.exe -m nbconvert --to notebook --execute D:\Lab2\notebooks\main.ipynb --ExecutePreprocessor.kernel_name=lab2 --ExecutePreprocessor.timeout=1800 --output main.executed.ipynb --output-dir D:\Lab2\outputs\environment
   - Lượt sandbox không tạo kernel/report, không có log tiến độ; đã đọc process để kiểm tra và gửi Ctrl+C ngắt (exit1). Chưa xác minh nguyên nhân sâu, không quy kết lỗi mô hình.
   - Chạy lại đúng lệnh ngoài sandbox: notebook thực thi thành công exit0, tạo main.executed.ipynb.
   - Runtime có cảnh báo ZMQ dùng selector thread trên Windows và kernel TCP không mã hóa; không sửa cấu hình ngoài phạm vi.
   - Notebook execution_count [1,2,3], không có output_type=error; nội dung source khớp notebook đã duyệt.

## Bằng chứng benchmark thật

- Report: [report.json](../outputs/environment/20261030T051457060333Z/report.json).
- Notebook đã chạy: [main.executed.ipynb](../outputs/environment/main.executed.ipynb).
- Thời gian report: 12:14:57–12:15:11, ngày 2026-10-30 Asia/Saigon; report lưu UTC.
- Fixture synthetic-v1, seed42, shape [8,3,224,224], nhãn int64, 6 lớp. CPU/XPU có cùng fixture SHA256 f223849e9e8358e08f8c76858ad5a66516b6e489ec3988b26faa35dad81c5867.
- DenseNet121 weights=None, freeze backbone/eval, train classifier, SGD lr0.01; CPU 14 threads; 3 warm-up và 10 bước đo mỗi thiết bị; synchronize XPU.
- Batch8 thành công cả hai, không OOM, không thực hiện nhánh batch4 trên phần cứng thật.
- CPU mean_step_seconds=0.3882185399881564; Intel Arc XPU=0.08989660000661388.
- Cả hai: status PASSED, shape [8,6], loss hữu hạn, backbone_unchanged=true, classifier_updated=true, tensorboard_verified=true.
- Mỗi thiết bị đã xác minh bằng EventAccumulator: 13 scalar loss và 10 scalar step_seconds.
- TEST-001/002/004 PASS trong notebook thật; TEST-003 PASS ở các unittest kiểm tra nhánh lỗi; TEST-005 PASS bằng notebook đúng kernel/source thực, traceback ở test lỗi và đọc được TensorBoard events. Chưa mở giao diện TensorBoard.
- Tỉ lệ CPU/XPU trong lượt đo này khoảng 4.32. Không suy rộng thành thời gian huấn luyện full dataset hoặc độ chính xác pretrained.

## Đối chiếu sau chạy

- Hash source/config trong report vẫn khớp file hiện tại; không dùng kết quả stale.
- Lần kiểm tra hậu kỳ đầu dùng read_text() không chỉ rõ UTF-8 cho notebook: AssertionError khi đối chiếu ký tự Unicode. Đọc lại bằng UTF-8 xác nhận toàn bộ notebook khớp; đây là lỗi lệnh kiểm tra hậu kỳ, không phải thay đổi file hoặc lỗi benchmark.
- Kiểm tra cuối với UTF-8: approved_sources_match=true, notebook_errors=[], execution_counts=[1,2,3], source_matches=true.
- Một lần soạn nhật ký qua công cụ lỗi cú pháp JavaScript trước khi ghi; đã soạn lại, không ảnh hưởng code/output.
- Cập nhật PROJECT_STATE và tạo log này; giữ nguyên WF LOCKED và hồ sơ phê duyệt.

## Giới hạn và bước tiếp theo

- Đây là một benchmark ngắn, classifier-only, fixture tổng hợp, weights ngẫu nhiên; không có kết quả accuracy hoặc full fine-tuning.
- Dataset/weights chưa tải, không cài thêm package. Không tự thực hiện các workflow dữ liệu/huấn luyện mới.
- Chờ người dùng nghiệm thu WF-001; sau đó đề xuất WF riêng cho kiểm kê/chia dữ liệu, pretrained models và thiết kế thí nghiệm.

