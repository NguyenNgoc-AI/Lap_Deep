# LOG-003 — Phương án chạy toàn bộ trên máy

- Ngày: 2026-10-30 (Asia/Saigon). REQ-003: nếu không dùng Colab, chạy toàn bộ trên máy thì sao?
- Trạng thái: NO_CODE_CHANGE. WF/GATE A và CHG/GATE B: chưa có/chưa duyệt.
- Đọc PROJECT_STATE.md và danh sách history. Kế thừa số liệu khảo sát ở LOG-002, không đo lại phần cứng.
- Nguồn đã đọc: https://docs.pytorch.org/docs/2.15/notes/get_start_xpu.html (được chuyển hướng từ stable).
- FACT: bảng phần cứng được kiểm chứng có Core Ultra với Intel Arc (Meteor Lake-H), Windows 11; tài liệu mô tả backend XPU hỗ trợ training/inference, yêu cầu chuẩn bị driver và kiểm tra torch.xpu.is_available().
- Giới hạn: chưa xác minh phiên bản Windows, driver và PyTorch thực tế, chưa chạy batch training trên GPU của người dùng. Danh sách hỗ trợ không phải bằng chứng môi trường hiện tại đã chạy được.
- PROPOSAL/PENDING: chạy toàn bộ trong D:\Lab2, venv riêng, notebook local và TensorBoard local; ưu tiên XPU khi đã qua kiểm chứng, CPU là lựa chọn dự phòng được ghi rõ. Không âm thầm chuyển thiết bị giữa các thí nghiệm.
- Khởi đầu transfer learning đóng băng backbone, batch nhỏ 8 hoặc 16 như cấu hình thử nghiệm; chạy từng mô hình, đo thời gian và bộ nhớ trước khi tăng batch/fine-tune. Dữ liệu đọc theo batch, không nạp toàn bộ vào RAM.
- Có thể hoàn thành mục tiêu bài bằng môi trường local; mức thời gian thực tế chưa biết. Chạy local chủ động lưu kết quả và không phụ thuộc quota cloud, nhưng cần quản lý bộ nhớ, điện/nhiệt và checkpoint. Dataset/weights vẫn cần tải ban đầu.
- Làm rõ đề xuất trước: Colab là một lựa chọn tiện lợi; không có bằng chứng bắt buộc phải dùng cloud hoặc GPU local không thể train.
- File tạo: D:\Lab2\history\2026-10-30_002_phuong-an-local.md. File cập nhật: D:\Lab2\PROJECT_STATE.md (bổ sung đề xuất, giữ lịch sử Colab).
- BEFORE/AFTER code: không áp dụng. Không cài package/driver, tải dữ liệu/weights, sửa code/config hoặc chạy training. Test kỹ thuật: NOT_RUN. Kiểm chứng tài liệu bằng đọc lại sau ghi.
- Không tạo commit/checkpoint hoặc rollback; chưa kiểm tra lại Git. Các lựa chọn local vẫn PENDING; chưa suy diễn câu hỏi thành duyệt WF/CHG.
- Bước tiếp theo đề xuất: WF cho kiểm tra môi trường local, setup và benchmark nhỏ, rồi chốt kế hoạch thực nghiệm dựa trên kết quả.
