# PROJECT_STATE — Lab 2

- Cập nhật: 2026-10-30, Asia/Saigon. Workspace: D:\Lab2.
- Rules đã đọc: C:\Users\toite\Downloads\Rules_29-10.md v1.0; tài liệu gốc giữ nguyên.
- WF-001: COMPLETED / ACCEPTED theo xác nhận trước của người dùng. Môi trường local và benchmark có bằng chứng trong outputs/environment/ và LOG-008/009.
- WF-002: IMPLEMENTATION COMPLETED / VERIFIED. Chỉ thị “Thực hiện đến khi xong đi” cho phép triển khai liên tục CHG-003..007; không dừng duyệt từng file. Chưa ghi nhận người dùng nghiệm thu kết quả cuối.
- Workflow khóa: workflows/WF-002_v1.0_LOCKED_intel-experiments.md. Ngoại lệ có evidence: workflows/WF-002_AMENDMENT-01_label-conflicts.md. Không sửa bản khóa.

## Kết quả

- Đủ 7 run, 33 epoch trên Intel Arc XPU. R01–R06: transfer 5 epoch/run; R07: fine-tune thêm 3 epoch từ checkpoint R02.
- Model cuối R07 VGG11 fine-tune được chọn bằng validation **92,03%** trước test; test **92,80% (2.784/3.000)**, macro-F1 **0,9297**.
- Best transfer VGG11 R02: validation91,53%, test91,70%, macro-F1 0,9186.
- Best transfer DenseNet121 R06: validation91,21%, test91,53%, macro-F1 0,9168.
- Test chỉ đánh giá R02/R06/R07 sau khóa lựa chọn. Notebook dùng lại kết quả test đã xác minh, không chạy lại để tuning.
- Dataset Intel Image Classification v2: 14.034 train gốc; manifest sau audit gồm 11.208 train, 2.798 validation, 3.000 test; 7.301 ảnh chưa có nhãn không dùng tính điểm.
- 13 nhóm ảnh giống byte nhưng khác nhãn (26 ảnh:23train/3test). Cách ly23train, tổng loại28train kể cả trùng/chồng lấn; giữ nguyên raw và test. Chi tiết outputs/data/audit.json, label_conflicts.json.

## Kiểm chứng

- 12 unit tests PASS: environment, leakage, conflict policy, corrupt images, ZIP traversal, weighted metrics, resume weights/epoch, stale config và confusion metrics.
- Preflight 8 tổ hợp architecture/mode/batch trên XPU PASS; đầu ra [B,6], gradient hữu hạn, frozen parameters và buffers không đổi.
- Kiểm tra artifact PASS: 7 run/33 epoch, checkpoint hashes, 6 scalar tags/run khớp history, 3 confusion matrix mỗi cái tổng3.000, metrics khớp prediction CSV, selection trước test.
- Notebook thực thi 5 code cells, không error, có ảnh nhúng. Source notebook giao nộp khớp source notebook đã chạy.
- Source/config/requirements huấn luyện khớp snapshot trước training. Không sửa source hoặc config giữa các run.
- Visual QA: learning curves và confusion matrix R07 đọc được, không bị cắt nhãn. Các metrics từng lớp có trong CSV.
- pip check PASS sau cài matplotlib; dependency versions/freeze được lưu. Không có thay đổi package trong quá trình huấn luyện.

## Môi trường và cách mở

- Intel Core Ultra5 125H / Intel Arc, RAM khoảng15,5GB; Windows11 25H2 64-bit; driver32.0.101.9150.
- Python3.14.5 tại D:\Lab2\.venv\Scripts\python.exe.
- torch2.14.1+xpu, torchvision0.29.1+xpu, tensorboard2.21.0, notebook7.6.3, ipykernel7.4.0, matplotlib3.11.2. Versions đầy đủ: outputs/dependencies.freeze.txt và identity từng run.
- README.md có lệnh notebook, pipeline CLI, tests và TensorBoard. TensorBoard đã mở tại http://127.0.0.1:6006; nếu tiến trình dừng, chạy lại lệnh trong README.

## Bàn giao

- Báo cáo: outputs/report/report.md; summary.json; bảng CSV; learning_curves.png và confusion matrices.
- Notebook nguồn: notebooks/main.ipynb. Bản đã chạy: outputs/notebooks/main.executed.ipynb.
- Phân tích đề: docs/phan_tich_de.md; nhận xét sâu từ kết quả: docs/nhan_xet_ket_qua.md.
- Checkpoint cuối: outputs/experiments/R07/best.pt. Tất cả runs có identity/history/best/last và TensorBoard.
- Bằng chứng kiểm chứng: outputs/unit_tests.json, outputs/verification.json, outputs/models/preflight.json.
- Backup và hashes: history/checkpoints/CHG-003_007_before, CHG-003_007_after (trước training), CHG-003_007_final (bản giao).
- Nhật ký triển khai: history/2026-10-30_009_trien-khai-wf002.md (LOG-010). Các LOG trước giữ nguyên. Không có Git repo, không tạo commit.

## Giới hạn / công việc còn lại

Không còn hạng mục triển khai hoặc kiểm chứng trong phạm vi WF-002. Chỉ một seed, chưa có kiểm chứng đa seed hoặc ngoài dataset; SHA256 không phát hiện toàn bộ ảnh gần giống. R07 có ngân sách học thêm3epoch. Không tự tuyên bố người dùng đã nghiệm thu.

## WF-003 / CHG-008 — Notebook 16 bước (hoàn tất)

Yêu cầu mới: một notebook theo đúng16bước. File giao: notebooks/intel_pipeline_16_steps.ipynb, có output thực,17codecells và16section, chạy thành công. Dùng dữ liệu/source/checkpoint trong D:/Lab2. Không sửa WF002/raw/models/config.

Bổ sung EDA,majoritybaseline,CV5fold linear-probe trên DenseNet121 ImageNet đóng băng (không phải CV R07),14.006 OOF; thống kê Wilson/pairedbootstrap/McNemar; lỗi thật và2GradCAM. Kiểm chứng tại outputs/pipeline_16_steps/delivery_verification.json; LOG011. Original delivery hashes không đổi.

## CHG-009 — Biên tập nội dung phân tích

Đã viết lại thuyết minh16bước trong notebooks/intel_pipeline_16_steps.ipynb theo yêu cầu người dùng: phân tích phương pháp/kết quả thay ghi chú quy trình. Giữ nguyên code,outputs,metadata và các chỉnh sửa bố cục hiện có của người dùng. Kiểm chứng tại outputs/pipeline_16_steps/editorial_verification.json; LOG012. Không cần thực thi lại vì chỉ sửaMarkdown.

## CHG-010 — Nguồn và tổng quan dataset

Notebook16bước hiện tại: notebooks/lab2.ipynb (tên mới phát hiện từ file thực tế). Đã thêm linkKaggle, overview/sáu lớp/số lượng/kích thước, cấu trúc thư mục và lệnh tải/chuẩn bị dữ liệu. Giữ toàn bộ cell cũ và output. LOG013; outputs/pipeline_16_steps/dataset_overview_verification.json PASS.

## CHG-011 — Biểu đồ best runs

Đã bổ sung4biểuđồ cóoutput vào cuối mục09 của notebooks/lab2.ipynb; R07 vàbesttransferR02/R06 được chọn bằngvalidationaccuracy. Giữcác cellcũ, khôngtrainlại. LOG014 và outputs/pipeline_16_steps/best_curves/verification.json PASS.

## WF-004 / CHG-012 — R07 mở rộng đủ5epoch (COMPLETED / VERIFIED)

R07_5epochs tiếp tục từepoch3, đãchạy4–5. Bestvalidationaccuracy epoch5=92,0658% (2576/2798), hơn R07gốc1ảnh; valloss0,26783, minvalloss epoch1=0,23784. Giữbestcheckpointmới riêng, chưa đánhgiátest. OriginalR07epoch3 vàtest92,80% giữnguyên. Notebooklab2.ipynb đã cập nhậtđồ thị5epoch vàgiảithíchlựa chọn/overfitting. LOG015; outputs/pipeline_16_steps/r07_5epochs/verification.json PASS.
