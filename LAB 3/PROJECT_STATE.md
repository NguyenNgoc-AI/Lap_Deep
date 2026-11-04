# PROJECT_STATE — Lab 3

Cập nhật: 2026-11-04, Asia/Ho_Chi_Minh.

## Rules và workflow

- Rules đang hiệu lực: `RULES.md` v1.1 của nhóm (ban hành 02/11/2026; bản trong `Lab2/RULES.md`, nhánh `lab2.1`).
- Lab 3 được làm từ 27/10 đến 01/11, **trước khi Rules v1.1 ban hành**, nên không có workflow (WF) hay phê duyệt GATE A/B được khóa trước khi viết code. Phiên 04/11 chỉ bổ sung tài liệu cho khớp Rules §11, §12, §19; không sửa code hay notebook. Không có WF-ID cho Lab 3.
- Nhật ký: `history/`. Các log trước 04/11 là **log ghi bù** từ lịch sử trò chuyện và commit Git, đánh dấu rõ trong từng file.

## Trạng thái phase

| Phase | Module | Trạng thái | Bằng chứng / ghi chú |
|---|---|---|---|
| P01 · Description | `docs/labs3-description.md` | IMPLEMENTED | 5W1H, input/output, luồng xử lý, đối chiếu 11 yêu cầu |
| P02 · Exercise 1 | `notebooks/ex1_sentiment_analysis.ipynb` | TESTED | Chạy trên GPU 28/10, output lưu trong notebook |
| P03 · Data | `src/data.py`, notebook ex2 bước 2–4 | IMPLEMENTED | Notebook đã tải và tokenize dữ liệu thật; script mới chạy với dữ liệu giả lập |
| P04 · Model | `src/model.py`, notebook ex2 bước 3 | IMPLEMENTED | Như trên |
| P05 · Training | `notebooks/ex2_finetuning.ipynb`, `src/train.py` | TESTED (notebook) / IMPLEMENTED (script) | Notebook chạy lại 04/11: 3 epoch, GPU, 121,8 giây, khớp code; script chưa chạy với dữ liệu thật |
| P06 · Evaluation | `src/evaluation.py`, notebook ex2 bước 7 | TESTED (notebook) / IMPLEMENTED (script) | Test 84.62%, F1 84.67%; dòng kết quả script `TODO` |
| P07 · Demo | `src/demo.py` | IMPLEMENTED | 4 chế độ chạy được với model giả lập; chưa chạy với model thật |
| P08 · Bàn giao | README, `AI_USAGE.md`, báo cáo, upload | IN PROGRESS | Chưa upload lên nhánh `Lab3` |

Chưa có phase nào ở trạng thái ACCEPTED: chưa ghi nhận nhóm/giảng viên nghiệm thu.

## Thay đổi quan trọng

| Ngày | Thay đổi | Điểm đối chiếu |
|---|---|---|
| 28/10 | Ex1, Ex2 bản đầu | Commit `4eaf9c8` "Thêm Lab 3", nhánh `Lab3` |
| 30/10 | Ex2 tách validation/test | Commit `38a9aa9` "Sửa ex2", nhánh `Lab3` |
| 01/11 | Xóa `LAB 3` khỏi `main` | Commit `4f1f92f`, nhánh `main` |
| 01/11 | Thêm `src/`, `docs/`, `AI_USAGE.md`, chuyển notebook vào `notebooks/` | Chưa commit (bản local) |
| 04/11 | Đổi tên `docs/lab3_description.md` → `labs3-description.md`, `plan_progress_status.md` → `plan-progress.md`; bổ sung nội dung theo Rules §19; thêm file này và `history/` | Chưa commit (bản local) |
| 04/11 | Chạy lại `notebooks/ex2_finetuning.ipynb` đủ 3 epoch trên GPU; điền kết quả chính thức vào `docs/`, README | Notebook lưu ở `D:\Code\Lap_Deep` (nhánh `Lab3`), chưa commit |

## Kiểm chứng

- Notebook Ex1, Ex2 bản đầu (28/10) và Ex2 bản hiện tại chạy lại 04/11: output thật, đã đối chiếu với tài liệu. Lần 04/11 trùng kết quả test và training loss với lần 28/10 (seed 42) → tái lập được.
- `src/`: `py_compile` PASS; chuỗi `data → model → train → evaluation → demo` exit 0 với model DistilBERT tí hon và dữ liệu giả lập offline. **Chưa chạy với model và dữ liệu thật.**
- Tài liệu: mọi con số trong `docs/`, README, `AI_USAGE.md` khớp output notebook (kiểm tra tự động); mọi link giữa các file `.md` mở được.

## Blocker và quyết định

- **Blocker:** không còn. Ex2 đã có kết quả chính thức (test 84.62%, F1 84.67%).
- **Đã chốt:** bài nộp ở nhánh `Lab3`; theo dõi bằng validation, test chỉ một lần; không đưa model fine-tune (~255 MB) lên GitHub.
- **Đề xuất, chờ nhóm xác nhận:** số liệu chính trong báo cáo lấy từ notebook (model cuối epoch 3); kết quả script (epoch tốt nhất, dự kiến epoch 2) là bổ sung khi chạy.

## Việc tiếp theo được đề xuất (chưa thực hiện)

1. Chạy các script `src` trên GPU; điền dòng kết quả script trong `docs/evaluation.md` và `docs/demo.md`.
2. Commit và push lên nhánh `Lab3`.
3. Thành viên khác bổ sung `AI_USAGE.md`.
