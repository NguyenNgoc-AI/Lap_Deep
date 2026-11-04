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
| P05 · Training | `notebooks/ex2_finetuning.ipynb`, `src/train.py` | **BLOCKED (chờ chạy lại)** | Bản sửa 30/10 chỉ có output 1 epoch trên CPU, không khớp `num_train_epochs=3`; bản đầu 28/10 đã chạy đủ 3 epoch |
| P06 · Evaluation | `src/evaluation.py`, notebook ex2 bước 7 | IMPLEMENTED | Kết quả cuối `PENDING_UPDATE` |
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

## Kiểm chứng

- Notebook Ex1 và Ex2 (bản đầu): output thật, đã đối chiếu với tài liệu.
- `src/`: `py_compile` PASS; chuỗi `data → model → train → evaluation → demo` exit 0 với model DistilBERT tí hon và dữ liệu giả lập offline. **Chưa chạy với model và dữ liệu thật.**
- Tài liệu: mọi con số trong `docs/`, README, `AI_USAGE.md` khớp output notebook (kiểm tra tự động); mọi link giữa các file `.md` mở được.

## Blocker và quyết định

- **Blocker:** kết quả cuối của Ex2 bản hiện tại chưa có — cần chạy lại trên máy GPU.
- **Đã chốt:** bài nộp ở nhánh `Lab3`; theo dõi bằng validation, test chỉ một lần; không đưa model fine-tune (~255 MB) lên GitHub.
- **Chưa chốt:** đánh giá bằng model cuối epoch 3 (notebook) hay epoch tốt nhất (script) cho số liệu chính trong báo cáo.

## Việc tiếp theo được đề xuất (chưa thực hiện)

1. Chạy lại `notebooks/ex2_finetuning.ipynb` và các script `src` trên GPU.
2. Điền kết quả cuối vào `docs/`, README, báo cáo; ghi log phiên chạy vào `history/`; cập nhật file này và `docs/plan-progress.md`.
3. Thành viên khác bổ sung `AI_USAGE.md`.
4. Upload `LAB 3/` lên nhánh `Lab3`.
