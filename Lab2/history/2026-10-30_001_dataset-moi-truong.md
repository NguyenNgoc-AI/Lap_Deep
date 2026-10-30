# LOG-002 — Dataset và đề xuất môi trường

- Ngày: 2026-10-30, Asia/Saigon. REQ-002. Trạng thái: NO_CODE_CHANGE.
- Người dùng chọn https://www.kaggle.com/datasets/puneet6060/intel-image-classification/data và yêu cầu đề xuất môi trường.
- APPROVED: lựa chọn dataset. PENDING: Colab GPU cho training, workspace chính D:\Lab2, local CPU cho kiểm tra nhỏ.
- WF/GATE A: chưa có/chưa duyệt. CHG kỹ thuật/GATE B: chưa có/chưa duyệt.

## Bằng chứng và thao tác chỉ đọc

- Đọc PROJECT_STATE.md và danh sách history; Rules đã đọc ở phiên trước vẫn trong ngữ cảnh.
- Đọc skill Ponytail 5.3.3 để chọn bộ phụ thuộc gọn.
- Get-CimInstance trong sandbox lỗi quyền truy cập CIM; chạy lại với yêu cầu quyền ngoài sandbox thành công.
- CPU: Intel Core Ultra 5 125H; GPU hệ thống liệt kê: Intel Arc Graphics; RAM_GB: 15.5 (làm tròn); D trống khoảng 164.2 GB.
- Lần đầu PowerShell tự định dạng bảng làm cột RAM không hiện; truy vấn riêng bằng ConvertTo-Json xác nhận 15.5 GB.
- Có lệnh python.exe/py.exe trong PATH; chưa xác minh runtime thực hoặc phiên bản package. Không suy diễn GPU NVIDIA từ máy này.
- Trang Kaggle mở được nhưng công cụ web không trích xuất được nội dung; chưa xác nhận số ảnh/split bằng file thật, chưa tải dataset.

## Phương án và phản biện

- Ưu tiên Google Colab GPU để thử nhiều mô hình; giữ notebook/module và hồ sơ chính tại D:\Lab2, đồng bộ kết quả/checkpoint về máy sau khi thực hiện theo WF được duyệt.
- Local đề xuất Python 3.11 hoặc 3.12 với venv riêng khi cần; cloud dùng Python sẵn có và ghi phiên bản thực tế. Bộ chính: torch, torchvision, tensorboard; Jupyter/ipykernel cho notebook local; matplotlib/scikit-learn nếu cần biểu đồ và chỉ số.
- Kiểm tra tương thích torch/torchvision trước khi khóa phiên bản. Chưa chốt lệnh cài hoặc phiên bản cụ thể.
- Intel GPU có backend XPU trong PyTorch; chưa kiểm chứng model GPU/driver/môi trường này. Không kết luận máy không thể train, cũng không hứa hiệu năng.
- Colab có GPU nhưng không bảo đảm loại GPU hoặc thời lượng; phải lưu checkpoint và kết quả ra nơi bền vững. Chưa có benchmark nên không dự đoán thời gian chạy.
- Không chọn thêm Docker/WSL/Conda trong phương án cơ sở vì chưa thấy nhu cầu của bài.
- Dataset sẽ kiểm kê nhãn, split, ảnh lỗi/trùng khi chuẩn bị dữ liệu; validation tách từ training, test dành cho đánh giá cuối.

## Nguồn tham khảo

- https://research.google.com/colaboratory/intl/en-GB/faq.html — Colab và giới hạn GPU/runtime.
- https://pytorch.org/get-started/locally/ — cài PyTorch và yêu cầu môi trường.
- https://docs.pytorch.org/docs/main/notes/get_start_xpu.html — backend Intel GPU.
- https://www.intel.com/content/www/us/en/developer/tools/oneapi/optimization-for-pytorch.html — native XPU.

## File và kiểm chứng

- Tạo D:\Lab2\history\2026-10-30_001_dataset-moi-truong.md; cập nhật D:\Lab2\PROJECT_STATE.md để ghi dataset, máy và đề xuất chưa duyệt.
- BEFORE/AFTER code: không áp dụng; không sửa code/notebook/config. Nhật ký cũ được giữ nguyên.
- Đọc lại tài liệu sau ghi để kiểm tra trạng thái. Test kỹ thuật: NOT_RUN. Chưa cài thư viện, tải weights/dataset, mở cloud runtime, upload hoặc train.
- Không có checkpoint/commit được tạo; không rollback. Không kiểm tra lại trạng thái đồng bộ Git trong phiên này.
- Tiếp theo: chốt môi trường rồi soạn WF cụ thể để duyệt; không coi yêu cầu đề xuất là quyền triển khai.
