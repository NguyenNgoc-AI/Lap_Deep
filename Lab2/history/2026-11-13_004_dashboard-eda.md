# Ngày 13/11/2026 · Bổ sung EDA vào dashboard

Theo yêu cầu bổ sung EDA trong dashboard của WF-LAB2-001, đã thêm liên kết điều hướng và mục EDA vào docs/data-visualization.html. Phạm vi phê duyệt trực tiếp là phần trình bày kết quả đã có. Bản HTML trước khi thêm EDA lưu tại thư mục làm việc riêng lab2-report/pre-eda.html của phiên.

Số ảnh theo lớp và kích thước lấy từ outputs/data/manifest.csv. Thống kê chất lượng dựa trên outputs/eda-seed42/train-quality.csv của bản chia ban đầu. Đối chiếu outputs/scene-review/review.csv, hai ảnh rừng trong cặp 301 trước thuộc train và validation, nay cùng nhóm trong validation. Cả hai ảnh JPEG được nhúng trực tiếp. Không chạy lại pipeline hoặc thay đổi dữ liệu.

Đã kiểm tra trong Edge ở độ rộng 390 và 1.440 px. Điều hướng EDA, sáu hàng phân bố, cả hai ảnh và phần chi tiết đều hoạt động. Kiểm lại 22 dòng epoch và việc bỏ ô đơn giá của phiên 003. Thay đổi lưu tại máy.
