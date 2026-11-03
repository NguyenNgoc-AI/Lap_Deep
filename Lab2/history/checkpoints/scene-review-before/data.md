# Dữ liệu

Nguồn [Intel Image Classification](https://www.kaggle.com/datasets/puneet6060/intel-image-classification/data). Lớp theo thứ tự chỉ số 0–5 là buildings, forest, glacier, mountain, sea, street. Ảnh có nhãn trong seg_train dùng để chia train/validation theo lớp với seed 42. seg_test giữ vai trò đánh giá. seg_pred dành cho demo.

Trong src/phases/phase_02_data.py, inspect_images đọc từng ảnh, còn rgb_digest tạo khóa từ kích thước và pixel RGB đã giải mã. make_split giữ bản test khi phát hiện ảnh giống hệt ở phía development. Cùng khóa nhưng khác nhãn thì cách ly các mẫu development liên quan. Sau khi loại các bản sao, hàm dành khoảng 20% mỗi lớp cho validation và kiểm tra không có khóa giao giữa các tập. Phương pháp này nhận diện ảnh giống hệt, không đo độ giống thị giác.

Đã kiểm tra nhận diện trùng và chia tập bằng fixture. Xem [nhật ký](../history/2026-11-03_008_rgb-digest.md) và [mô tả P01](labs2-description.md).

Đối chiếu chỉ đọc trên Intel local bằng inspect_images và make_split(seed=42, quarantine_conflicts=True): 14.034 ảnh development, 3.000 ảnh test. Có 23 mẫu development bị loại do xung đột nhãn, 5 do trùng nội bộ hoặc trùng test. Kết quả 11.208 train, 2.798 validation và 3.000 test. Kiểm tra tổng mẫu và không giao hash giữa ba split đạt. Lần này chia trong bộ nhớ, chưa xuất manifest chính thức.

### EDA sau chia tập

[Báo cáo EDA và hai biểu đồ](../outputs/eda-seed42/EDA.md) trình bày số mẫu từng lớp, tỷ lệ giữa các tập, kích thước, chế độ màu, ảnh bị loại và ví dụ train. Baseline lớp đa số chọn mountain từ train, đạt 500/2798 (17,87%) trên validation.

Xem thêm [phân bố train/validation/test và số ảnh không vuông theo từng lớp](../outputs/eda-seed42/theo-lop.png).
EDA mở rộng: [notebook](../notebooks/eda.ipynb) và [báo cáo tám mục](../outputs/eda-seed42/EDA.md). Có 48 cặp ứng viên train/validation, trong đó sáu cặp đã xem có cảnh gần như lặp lại. Cần rà nhóm và kiểm lại split trước normal run.
