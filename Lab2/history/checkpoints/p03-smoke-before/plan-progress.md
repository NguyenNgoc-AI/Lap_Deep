# Tiến độ Lab 2

| Bước | Trạng thái ngày 03/11/2026 | Bằng chứng hoặc điều kiện tiếp theo |
|---|---|---|
| Description | Đã chuyển Generate | [Mô tả Lab 2](labs2-description.md) và [workflow đã khóa](../workflows/WF-LAB2-001.md). |
| Generate | Đã triển khai phần nhận diện ảnh trùng của P01 | [CHG-DATA-001](../workflows/CHG-DATA-001.md). [CHG-DATA-002](../workflows/CHG-DATA-002.md) chờ duyệt. |
| Smoke run | Kiểm tra riêng CHG-DATA-001 đạt | [Nhật ký](../history/2026-11-03_008_rgb-digest.md). Smoke toàn pipeline chưa chạy. |
| Normal run | Chưa chạy | Chạy cấu hình đã chốt sau khi smoke run đạt. |
| Check against description | Chờ kết quả thực thi | Ghi PASS/FAIL kèm bằng chứng theo từng tiêu chí. |
P01 · EDA đã thực hiện theo tám mục. Bản chia hiện có rủi ro gần trùng giữa các tập. Xem [báo cáo EDA](../outputs/eda-seed42/EDA.md) trước khi chốt manifest.
P01 · Đã xử lý điều kiện gần trùng ở dòng trên. [Bản chia theo nhóm cảnh](../outputs/scene-review/report.md) đã vượt kiểm tra nhóm, hash, test và batch. Chưa train.
P02 · Đã kiểm tra hai kiến trúc và freeze bằng batch thật trên XPU. [Số tham số và bằng chứng](model.md). Smoke training hai stage còn ở P03.
