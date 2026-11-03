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
P03 · Smoke hai stage đã PASS cho cả hai model. Xem docs/training.md. Normal chưa chạy.
P03 · Entry point chung đã kiểm tra smoke, resume từ epoch 6, patience, hai model và nhánh LR. Normal chưa chạy. Xem outputs/smoke-entry-p03/checks.json.

Normal run P03 hoàn tất trên XPU. VGG11: 10 epoch, best 7 đạt 2.611/2.793. DenseNet121: 12 epoch, best 9 đạt 2.613/2.793, loss 0,1878. Nhánh VGG LR 3e-6: 5 epoch bổ sung, best 9 đạt 2.597/2.793. Đã reload best và đối chiếu log cả ba lượt. Chọn DenseNet121 trước khi dùng test. [Báo cáo và đường học](../outputs/training-scene-v1/TRAINING.md).
P04 hoàn tất: DenseNet121 epoch 9 test accuracy 93,10%, macro-F1 93,26%. Báo cáo outputs/evaluation-scene-v1/report.md. Main notebook đã chạy lại từ kết quả lưu. P05 demo là bước kế tiếp.
