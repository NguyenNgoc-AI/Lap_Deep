# Phiên 2026-11-01_001 · Tổ chức lại Lab 3: src, docs, AI_USAGE, báo cáo

> **Log ghi bù** ngày 04/11/2026 từ lịch sử trò chuyện.

- **Người thực hiện:** HuHoww, có Claude hỗ trợ. **WF:** không có (Rules v1.1 ban hành 02/11). **Trạng thái:** IMPLEMENTED (bản local, chưa commit).

## Diễn biến

1. Xóa thư mục `LAB 3` khỏi nhánh `main` vì đã có ở nhánh `Lab3` (commit `4f1f92f`).
2. Đọc repo: Lab 1 (`README.md`, `AI_USAGE.md`), Lab 2 (`docs/`, `PROJECT_STATE.md`, `src/phases/`). Phát hiện ex2 trên nhánh `Lab3` là bản sửa 30/10, khác bản đã dùng → thay bằng bản này.
3. Viết `src/`: `config.py`, `data.py`, `model.py`, `train.py` (theo dõi validation, giữ epoch tốt nhất), `evaluation.py` (đổi tên từ `evaluate.py` để không trùng thư viện `evaluate`), `demo.py`.
4. Theo danh sách giảng viên ghi trên bảng: tạo `docs/` gồm description, data, model, training, evaluation, demo, plan/progress; thêm `AI_USAGE.md` theo mẫu Lab 1; chuyển notebook vào `notebooks/`; viết README, `requirements.txt`, `.gitignore`.
5. Tạo báo cáo Lab 3 (tài liệu Claude Docs, xuất được Word/PDF).

## Kiểm thử

- `python -m py_compile src/*.py`: PASS.
- Chuỗi `src.data → src.model → src.train → src.evaluation → src.demo` với model DistilBERT tí hon (32 chiều, 1 lớp) và 560 câu giả lập offline: exit 0, tạo 8 file trong `results/`. Lỗi gặp và đã sửa: CSV thiếu `ClassLabel`; `train_loss` rỗng khi số bước/epoch < `logging_steps`.
- **Chưa chạy với model và dữ liệu thật** (môi trường kiểm thử không truy cập được Hugging Face Hub).
- Đối chiếu tự động mọi con số trong tài liệu với output notebook: khớp.

## Vấn đề còn tồn tại

- Ex2 bản 30/10 cần chạy lại; kết quả cuối `PENDING_UPDATE`.
- Nhánh `Lab2` (và sau này `lab2.1`) vẫn chứa thư mục `LAB 3/` cũ.
