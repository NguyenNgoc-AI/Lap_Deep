# Bản chia theo nhóm cảnh · seed 42

Đã rà 356 cặp trong near-pairs.csv bằng chín trang ảnh, đánh số từ 1. Trong review.csv, page chỉ trang và pair_id chỉ số phía trên cặp. Có 62 cặp cùng cảnh, 265 cặp khác cảnh, 29 cặp chưa chắc. Dấu hiệu cùng cảnh là bố cục và vị trí chi tiết khớp. Đường chân trời tương tự đơn thuần không đủ xác nhận. Các tập dùng chung manifest này.

| Lớp | Train | Validation | Test |
|---|---:|---:|---:|
| buildings | 1749 | 437 | 437 |
| forest | 1809 | 452 | 474 |
| glacier | 1914 | 479 | 553 |
| mountain | 2002 | 500 | 525 |
| sea | 1799 | 450 | 510 |
| street | 1900 | 475 | 501 |
| Tổng | 11173 | 2793 | 3000 |

Baseline luôn đoán mountain, đúng 500/2793 (17.90%).

Loại theo thứ tự ưu tiên: 28 ảnh đã loại ở bước trùng tuyệt đối/xung đột nhãn; thêm 18 ảnh development thuộc nhóm chạm test, 22 ảnh development vì có cặp chưa chắc. Nếu lý do chồng lấn, chỉ ghi lý do ưu tiên. Giữ đủ 3.000 đường dẫn test gốc. Không đổi nhãn, không xóa ảnh gốc.

Đọc lại manifest qua run() và DataLoader: cả ba tập cho batch (8,3,224,224). Có 0 nhóm hoặc khóa RGB xuất hiện ở hai tập, 0 cặp cùng cảnh hoặc chưa chắc còn nằm chéo tập. Còn 100 cặp ứng viên nằm chéo tập được phân loại khác cảnh. Phạm vi kiểm tra là các ứng viên dHash ≤3, không bảo đảm phát hiện mọi góc chụp khác của cùng địa điểm.

SHA-256 manifest: b90d99ee2d0c221171bbc8127c695fa938b4415fd39437b658cc11f9eab7b19a. [Manifest](../data/manifest.csv) · [Mẫu bị loại](../data/excluded.csv) · [Bảng rà từng cặp](review.csv) · [Mã tái tạo](build_manifest.py). Dùng python outputs/scene-review/build_manifest.py <thư_mục_mới> để tái tạo vào thư mục chưa tồn tại.
