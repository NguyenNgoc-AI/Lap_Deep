# PROJECT_STATE — Lab 2

- Cập nhật: 2026-10-30 (Asia/Saigon).
- Workspace: D:\Lab2.
- Rules đã đọc: C:\Users\toite\Downloads\Rules_29-10.md, v1.0, FINAL / APPROVED / LOCKED theo nội dung tài liệu. Chưa sao chép Rules vào workspace.
- REQ-001: đọc Rules và phân tích đề trong ảnh — đã phân tích; NO_CODE_CHANGE.
- WF-001 v1.0: [Chuẩn bị môi trường local — LOCKED](workflows/WF-001_v1.0_LOCKED_local-environment.md), COMPLETED; người dùng nghiệm thu bằng tin nhắn “ok làm đi” ngày 2026-10-30 sau báo cáo kết quả. Bản khóa giữ nguyên, trạng thái thực thi/acceptance ghi tại State và LOG-009.
- WF-002 v1.0: [Dữ liệu và thực nghiệm Intel](workflows/WF-002_v1.0_DRAFT_intel-experiments.md), UNDER_REVIEW; GATE A PENDING. Đề xuất VGG11/DenseNet121, sáu run transfer + một run fine-tune.
- CHG-001: [Đề xuất venv và thư viện](workflows/CHG-001_PROPOSED_environment.md), GATE B APPROVED bằng tin nhắn “ok” ngày 2026-10-30; IMPLEMENTED / TESTED cho phạm vi cài đặt và kiểm tra sơ bộ. Bản đề xuất giữ nguyên như hồ sơ trước phê duyệt.
- CHG-002: [Phase, notebook và test](workflows/CHG-002_PROPOSED_phase-notebook-tests.md), GATE B APPROVED bằng tin nhắn “ok” ngày 2026-10-30; IMPLEMENTED / TESTED. Ba file đúng AFTER, 5 unittest PASS, notebook benchmark thật PASS.
- PHASE-01: src/phases/phase_01_environment.py và notebooks/main.ipynb — ACCEPTED ngày 2026-10-30. Contract synthetic-v1 theo WF.
- Kiểm tra CHG-001: PASS — pip check không có dependency lỗi; import thư viện thành công; tensor CPU và Intel Arc XPU cùng trả [2.0,2.0], xpu_available=True. TEST-001..005 của WF-001 đã có bằng chứng từ notebook, test lỗi và TensorBoard EventAccumulator; xem LOG-008.
- Git/checkpoint: workspace ban đầu trống, không có .git; chưa có commit/checkpoint.
- Nhật ký: [LOG-001](history/2026-10-29_001_phan-tich-de.md).
- Nhật ký tiếp theo: [LOG-002](history/2026-10-30_001_dataset-moi-truong.md).
- REQ-002: người dùng chọn Intel Image Classification tại https://www.kaggle.com/datasets/puneet6060/intel-image-classification/data và yêu cầu đề xuất môi trường.
- Dataset: APPROVED theo lựa chọn trực tiếp của người dùng; metadata Kaggle xác nhận currentVersionNumber=2 và sáu lớp. Chưa tải/kiểm kê file; số ảnh thực sẽ xác minh ở PHASE-02.
- Máy đã khảo sát: Intel Core Ultra 5 125H, Intel Arc Graphics, RAM hệ thống khoảng 15.5 GB; ổ D trống khoảng 164.2 GB trước cài đặt. Benchmark DenseNet121 classifier-only batch8: CPU 0.3882 s/bước, XPU 0.0899 s/bước (khoảng 4.32 lần trong lượt đo này); không OOM.
- DECISION-001 / REQ-004: APPROVED — người dùng chốt chạy toàn bộ local tại D:\Lab2, ưu tiên Intel GPU qua XPU, CPU dự phòng. Môi trường Python riêng, notebook và TensorBoard local. Phương án Colab trước đây không được chọn. Đã cài thư viện CHG-001; chưa tải/upload dataset hoặc weights.
- Bối cảnh REQ-003: [LOG-003](history/2026-10-30_002_phuong-an-local.md). Quyết định chốt: [LOG-004](history/2026-10-30_003_chot-local-va-wf.md).
- Khảo sát sau GATE A: Windows 11 25H2 64-bit (build 26200); Python 3.14.5 64-bit hiện có, pip 26.1.1; driver Intel Arc 32.0.101.9150. Python hiện có có wheel XPU tương ứng, đề xuất dùng lại thay vì cài thêm Python 3.12.
- Đã cài và import thành công: torch 2.14.1+xpu, torchvision 0.29.1+xpu, tensorboard 2.21.0, notebook 7.6.3, ipykernel 7.4.0. Python tại D:\Lab2\.venv\Scripts\python.exe. requirements khớp AFTER, SHA256 71E75C313BC808DBE5CA86B0B6C54C4C90D64786E5815BA33D6A4303DD00DCA2.
- Bằng chứng và phê duyệt mới: [LOG-005](history/2026-10-30_004_duyet-wf-khao-sat-chg001.md).
- Bằng chứng cài đặt và pip freeze: [LOG-006](history/2026-10-30_005_cai-dat-kiem-chung-chg001.md). Benchmark tại LOG-008; nghiệm thu tại LOG-009.
- Phiên chuẩn bị CHG-002: [LOG-007](history/2026-10-30_006_de-xuat-chg002.md).
- Triển khai CHG-002: [LOG-008](history/2026-10-30_007_trien-khai-kiem-chung-chg002.md). [Report thật](outputs/environment/20261030T051457060333Z/report.json), [notebook đã chạy](outputs/environment/main.executed.ipynb). Source/config hashes khớp; cùng fixture CPU/XPU, classifier cập nhật và backbone giữ nguyên. TensorBoard mỗi thiết bị có 13 loss + 10 timing scalar.
- Nghiệm thu WF-001 và chuẩn bị WF-002: [LOG-009](history/2026-10-30_008_nghiem-thu-wf001-de-xuat-wf002.md). Ổ D trống khoảng 160 GB trước khi tải dataset/weights.

## Yêu cầu đã xác định từ ảnh

Thử các kiến trúc pretrained, khảo sát layer/tham số, thay classification layer, chuẩn bị transforms/DataLoader, huấn luyện, thử hyperparameter, theo dõi TensorBoard và đánh giá test set.

## Chưa chốt

WF-002 đề xuất VGG11 và DenseNet121, chia train/validation 80/20 từ training sau kiểm tra trùng lặp, test giữ đến cuối; baseline Adam lr0.001 batch8, biến thể lr0.0003 hoặc batch16, 5 epoch/run; fine-tune run thắng thêm 3 epoch lr0.00001. Tất cả là PENDING GATE A, chưa phải cấu hình được duyệt. Số ảnh/split cần kiểm kê local; chưa có ETA thực hoặc kết quả accuracy.

## Bước tiếp theo được đề xuất

Duyệt WF-002 v1.0 tại GATE A; sau đó trình CHG theo phase với BEFORE/AFTER ở GATE B. Chưa tải dataset/weights, sửa notebook hoặc bắt đầu training thật trong phiên soạn workflow.
