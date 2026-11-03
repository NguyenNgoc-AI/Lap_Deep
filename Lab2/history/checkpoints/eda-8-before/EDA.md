# EDA sau chia tập · Intel Image Classification

Kết quả tính từ ảnh local bằng inspect_images và make_split (seed 42), trước huấn luyện. Tỷ lệ phần trăm dưới đây dùng tổng ảnh của từng cột làm mẫu số.

| Lớp | Train | Validation | Test |
|---|---:|---:|---:|
| buildings | 1750 (15.61%) | 437 (15.62%) | 437 (14.57%) |
| forest | 1816 (16.20%) | 453 (16.19%) | 474 (15.80%) |
| glacier | 1919 (17.12%) | 479 (17.12%) | 553 (18.43%) |
| mountain | 2004 (17.88%) | 500 (17.87%) | 525 (17.50%) |
| sea | 1818 (16.22%) | 454 (16.23%) | 510 (17.00%) |
| street | 1901 (16.96%) | 475 (16.98%) | 501 (16.70%) |
| **Tổng** | **11208** | **2798** | **3000** |

![Phân bố lớp](phan-bo.png)

Lớp lớn nhất trong train là **mountain**. Baseline luôn đoán lớp này sẽ đúng **500/2798 = 17.87%** trên validation. Tỷ số số mẫu lớp lớn nhất/nhỏ nhất của train là 1.15. Mỗi lớp đều được đại diện và chênh lệch tỷ trọng lớn nhất giữa train và validation chỉ là 0.02 điểm phần trăm. Chưa có căn cứ từ số lượng lớp để áp dụng oversampling. Khi đánh giá cần xem thêm recall và F1 theo lớp.

| Tập | Ảnh 150×150 | Rộng min–max | Cao min–max | Chế độ màu |
|---|---:|---:|---:|---|
| train | 11168/11208 | 150–150 | 76–150 | {'RGB': 11208} |
| validation | 2790/2798 | 150–150 | 102–150 | {'RGB': 2798} |
| test | 2993/3000 | 150–150 | 72–150 | {'RGB': 3000} |

Kích thước đầu vào của hai model là 224×224. Resize giúp tạo batch đồng nhất nhưng không thêm chi tiết cho ảnh gốc nhỏ. Cần dùng cùng phép biến đổi xác định cho validation và test.

Đã giải mã 14034 ảnh development và 3000 ảnh test. Loại 28 ảnh development. Trong đó 23 ảnh thuộc nhóm mâu thuẫn nhãn. Trong 5 ảnh còn lại, 0 ảnh trùng test và 5 ảnh trùng nội bộ development. Ba tập không giao khóa RGB. Test giữ nguyên, có 0 bản lặp ngoài ảnh đầu tiên khi nhóm theo khóa RGB. Kiểm tra chỉ phát hiện ảnh giống hệt sau giải mã.

seg_pred có 7301 file, không có nhãn để tính phân bố lớp hay baseline.

![Ảnh mẫu train](mau-train.png)

Ảnh mẫu được chọn từ train. Bảng test chỉ mô tả thành phần dữ liệu, không dùng để chọn model hoặc siêu tham số.

## Phân bố trong từng lớp

![Phân bố theo lớp](theo-lop.png)

Mỗi hàng lấy tổng ảnh có nhãn của chính lớp đó làm mẫu số. Test là tập có sẵn của dataset. Chỉ phần development sau làm sạch được chia 80/20 thành train và validation. Trong 55 ảnh có chiều cao dưới 150 pixel, 21 ảnh thuộc glacier và 19 ảnh thuộc mountain. Tất cả ảnh đều rộng 150 pixel. [Bảng từng kích thước theo lớp và split](theo-lop.csv).
