# LOG-004 — Chốt local và soạn WF-001

- Ngày: 2026-10-30 (Asia/Saigon). REQ-004; DECISION-001.
- Chỉ thị người dùng: “Ok chôt với phương án này”. APPROVED: chạy toàn bộ local D:\Lab2, ưu tiên XPU, CPU dự phòng; venv/notebook/TensorBoard local.
- Trạng thái phiên: NO_CODE_CHANGE; ghi nhận quyết định và soạn workflow đề xuất.
- Đọc PROJECT_STATE.md, LOG-003 và danh sách file thực tế. Workspace hiện có tài liệu quản trị, chưa có code hoặc .git.
- Tạo workflows/WF-001_v1.0_DRAFT_local-environment.md (UNDER_REVIEW); phạm vi setup và benchmark nhỏ, chưa train dữ liệu thật. GATE A cho chi tiết WF: chưa duyệt; GATE B: chưa có CHG.
- Cập nhật PROJECT_STATE.md: lựa chọn local APPROVED, Colab không chọn, liên kết WF và log. Giữ nguyên log cũ.
- Đề xuất benchmark DenseNet121 random weights, 6 lớp, frozen backbone, dữ liệu tổng hợp, batch 8 (4 nếu OOM), 3 warm-up + 10 bước đo mỗi thiết bị. Mục đích đo khả năng môi trường; không thay cho đánh giá pretrained hoặc test set.
- Phản biện: xác nhận phương án local không tự động duyệt chi tiết file/lệnh cài chưa được trình. Không cần hỏi lại người dùng lựa chọn local; chỉ trình WF cụ thể ở GATE A theo Rules mục 1 và 4.
- Chưa xác minh OS/driver/package hoặc benchmark. Test kỹ thuật NOT_RUN; không cài đặt, sửa driver, tạo code/notebook/config, tải dữ liệu/weights hoặc chạy training.
- BEFORE/AFTER code: không áp dụng. Tài liệu mới có BEFORE = chưa tồn tại; PROJECT_STATE cập nhật trạng thái thực, không sửa WF khóa.
- Kiểm chứng: đọc lại WF, trạng thái và log sau khi ghi; kiểm tra quyết định local và UNDER_REVIEW/GATE B chưa duyệt nhất quán.
- Không tạo checkpoint/commit, không rollback; workspace không có Git tại lần liệt kê này.
- Tiếp theo: người dùng duyệt WF-001; sau đó khảo sát phiên bản và trình CHG cụ thể. Các quyết định kiến trúc/thí nghiệm chính vẫn chưa chốt.
