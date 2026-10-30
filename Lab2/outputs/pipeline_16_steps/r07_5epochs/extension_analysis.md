### R07 mở rộng: đủ 5 epoch fine-tune

Ba epoch ban đầu là **ngân sách thực nghiệm dự kiến**, không phải kết quả early stopping hay bằng chứng mô hình đã hội tụ. R02 được chọn từ sáu run transfer vì có validation accuracy cao nhất (91,53%); R07 tiếp tục từ checkpoint này, mở block cuối và đạt 92,03% ở epoch fine-tune thứ3. Đây là cơ sở chọn R07 trong ma trận ban đầu.

Lượt mở rộng tiếp tục **epoch4–5 từ last.pt ở epoch3**, giữ optimizer, RNG, thứ tự lấy mẫu, LR1e-5 và batch8. Lịch sử ba epoch đầu được giữ nguyên, không huấn luyện lại. Tổng ngân sách của nhánh này gồm 5epoch transfer của R02 cộng 5epoch fine-tune, nên vẫn lớn hơn các run chỉ có 5epoch transfer.

| Epoch fine-tune | Train accuracy | Validation accuracy | Train loss | Validation loss |
|---:|---:|---:|---:|---:|
| 1 | 95.62% | 91.74% | 0.1211 | 0.2378 |
| 2 | 96.17% | 91.78% | 0.0989 | 0.2447 |
| 3 | 96.87% | 92.03% | 0.0837 | 0.2494 |
| 4 | 97.57% | 91.92% | 0.0708 | 0.2623 |
| 5 | 97.98% | 92.07% | 0.0614 | 0.2678 |

**Kết quả lựa chọn:** epoch5 có validation accuracy cao nhất **92,07%**, tương ứng2.576/2.798 ảnh đúng, hơn epoch3 đúng **1ảnh** (khoảng0,036điểm phần trăm). Epoch1 có validation loss thấp nhất **0,2378**. Trong khi train loss giảm còn0,0614, validation loss tăng lên0,2678 và khoảng cách train–validation accuracy gần5,92điểm phần trăm. Điều này cho thấy cải thiện accuracy rất nhỏ đi kèm dấu hiệu overfitting theo loss; chưa có cơ sở kết luận khả năng tổng quát hóa tốt lên một cách ổn định.

Checkpoint mở rộng chọn theo accuracy nằm tại `outputs/experiments/R07_5epochs/best.pt` (epoch5); mô hình và kết quả3epoch ban đầu vẫn lưu riêng. **Test accuracy92,80% và các kiểm định/Grad-CAM trước đó thuộc checkpoint R07 epoch3**, không phải epoch5. Lượt bổ sung được thực hiện sau khi đã xem test gốc, nên chỉ phân tích validation và chưa đánh giá test cho checkpoint mới.
