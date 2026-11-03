# Huấn luyện

**P03 · Phương án đề xuất ngày 03/11/2026.** Mỗi kiến trúc có một normal run gồm hai giai đoạn liên tiếp. Một epoch là một lượt qua toàn bộ tập train, sau đó đánh giá toàn bộ validation. Đánh số epoch liên tục từ 1 để đối chiếu đường học, log và checkpoint.

| Giai đoạn | Epoch trong run | Phần được học | Optimizer và learning rate đề xuất |
|---|---|---|---|
| Học đầu phân loại | 1–5, chạy đủ 5 | Chỉ lớp Linear sáu đầu ra của từng mạng | Adam, LR 0,0003 |
| Fine-tuning | 6–20, tối đa 15 | Linear mới cùng khối conv 5 của VGG11, hoặc dense block 4 và norm5 của DenseNet121 | Adam mới cho các tham số được mở, LR 0,00001 |

Hai model dùng cùng split, seed 42, batch size đề xuất 8, ảnh 224×224, cross-entropy và chính sách freeze trong [model.md](model.md). Giữ LR cố định trong từng giai đoạn. Năm epoch đầu cho hai classifier cùng cơ hội học nhãn mới. Mười lăm epoch sau là ngân sách để quan sát diễn biến validation khi mở backbone. Ở lần làm cũ, loss của VGG11 tăng trong khi accuracy thay đổi ít ở các epoch fine-tuning sau. Vì vậy điều kiện dừng cần được chốt trước khi chạy lại.

**Chuyển giai đoạn.** Sau epoch 5, nạp checkpoint của giai đoạn đầu có validation accuracy cao nhất. Nếu hòa, chọn loss thấp hơn rồi epoch sớm hơn. Ghi epoch nguồn vào log của epoch 6 và khởi tạo lại optimizer.

**Dừng và chọn checkpoint.** Trong giai đoạn 2, dùng validation loss của checkpoint chuyển tiếp làm mốc ban đầu. Nếu loss giảm ít nhất 0,0001 so với mốc, cập nhật mốc và đặt lại bộ đếm. Dừng khi có 3 epoch liên tiếp không đạt mức giảm đó hoặc đã hết epoch 20. Sau mỗi epoch hoàn tất, kể cả epoch kích hoạt dừng, cập nhật `best.pt` theo validation accuracy trên cả hai giai đoạn với cùng quy tắc hòa điểm. Lưu `last.pt` để tiếp tục training. Hai model có thể dừng ở các epoch khác nhau.

**Smoke run và log.** Trước normal run, dùng vài batch riêng để kiểm tra cả lớp được học, việc chuyển giai đoạn và khả năng lưu/nạp checkpoint. Mỗi normal run có log riêng theo run ID, stage, epoch, LR, thời gian, train/val loss, train/val accuracy, best epoch, việc lưu checkpoint và lý do dừng. TensorBoard dùng cùng số epoch với file log.

**Khảo sát learning rate.** Sau hai run chính, đề xuất thêm một nhánh VGG11 chỉ chạy lại giai đoạn 2 với LR 0,000003. Dùng đúng checkpoint chuyển tiếp của VGG11 và cùng dữ liệu, seed, batch, thứ tự lấy mẫu, ngân sách, quy tắc dừng/chọn. Hai run chính có ngân sách tối đa 40 epoch tổng cộng; nhánh phụ có ngân sách riêng tối đa 15 epoch.

**Ước lượng thời gian.** Ghi thời gian train và validation từng epoch theo model và stage. Ví dụ, nếu một epoch kể cả validation mất trung bình 5 phút, 40 epoch của hai run chính tương ứng khoảng 3 giờ 20 phút, chưa tính smoke run, I/O checkpoint và nhánh phụ. Cần cập nhật ước lượng bằng thời gian đo trên máy ở từng giai đoạn.

Nguồn tham khảo cho cách thay classifier và dùng mạng pretrained. Ngân sách epoch và LR trong bảng là đề xuất riêng cho Lab 2. [PyTorch Transfer Learning Tutorial](https://docs.pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

## P03 · smoke chuyển giai đoạn (03/11/2026)

Đã chạy hai model trên XPU với 24 ảnh train và 24 ảnh validation lấy từ manifest đã chia theo nhóm cảnh, mỗi lớp bốn ảnh ở mỗi tập. Mỗi epoch có ba batch, batch size 8. Mỗi model chạy đủ năm epoch chỉ học classifier (LR 3e-4), nạp handoff tốt nhất theo accuracy/loss/epoch, mở khối cuối và tạo Adam mới (LR 1e-5) để chạy thêm hai epoch. Dừng theo ngân sách smoke.

| Model | Handoff | Best | Số đúng sau reload | Loss sau reload (xấp xỉ) |
|---|---:|---:|---:|---:|
| VGG11 | 5 | 7 | 19/24 | 1,0263 |
| DenseNet121 | 5 | 7 | 9/24 | 1,5357 |

best.pt nạp vào model mới cho kết quả khớp log trên cùng 24 ảnh. last.pt đọc lại được trạng thái epoch 7, optimizer và RNG. TensorBoard có đủ bảy điểm validation khớp history. Chưa kiểm tra tiếp tục training sau khi ngắt tiến trình, hoặc kích hoạt patience 3. Đây là smoke qua script riêng gọi hàm epoch và checkpoint của phase cũ. Entry point normal hiện dùng R01–R07 và đối chiếu hash file với khóa pixel. Cần chuyển sang thiết kế hai run và xác minh bản normal trước khi huấn luyện toàn tập.
[Báo cáo máy](../outputs/smoke-p03/20261103-133427/report.json) · [Script smoke](../outputs/smoke-p03/run_smoke.py).

## Entry point dùng chung cho smoke và normal

Chạy từ D:/Lab2 bằng kernel local:
```powershell
.\.venv\Scripts\python.exe -m src.phases.phase_04_train --smoke
.\.venv\Scripts\python.exe -m src.phases.phase_04_train
```
Lệnh đầu dùng 24 ảnh train, 24 validation (4 ảnh/lớp), 5 epoch classifier + tối đa 4 epoch fine-tune. Lệnh sau dùng toàn train/validation, 5 + tối đa 15. Notebook main mặc định smoke. Các run normal lưu tại outputs/training-scene-v1, smoke tại outputs/smoke-entry-p03. Mỗi run có identity.json, run.log, history.json, TensorBoard, best.pt và last.pt. Hai run chính có thêm handoff.pt và branch-rng.pt. Nhánh LR của VGG bắt đầu từ cùng trọng số và trạng thái RNG trước epoch 6. Chỉ hai run chính được xét chọn. Entry point đối chiếu checksum manifest và pixel RGB của ảnh được dùng. Dữ liệu test thuộc bước đánh giá P04 riêng.

Smoke thực tế trên XPU: VGG11 dừng có chủ đích sau epoch 6, tiến trình mới nạp last.pt và chạy tiếp 7–9. Cả hai run chính và nhánh VGG đều chọn epoch 9 và nạp lại được best. Log TensorBoard trùng history cả số bước lẫn giá trị. Kiểm tra dừng sớm dùng DenseNet121 và LR bằng 0 trong thư mục kiểm thử riêng để tạo loss đứng yên trên ảnh thật. Bộ đếm lần lượt 1, 2, 3; dừng ở epoch 8 và giữ best epoch 5. Đây là kiểm tra cơ chế, không phải kết quả normal. [Bằng chứng](../outputs/smoke-entry-p03/checks.json).

Normal run P03 hoàn tất trên XPU. VGG11: 10 epoch, best 7 đạt 2.611/2.793. DenseNet121: 12 epoch, best 9 đạt 2.613/2.793, loss 0,1878. Nhánh VGG LR 3e-6: 5 epoch bổ sung, best 9 đạt 2.597/2.793. Đã reload best và đối chiếu log cả ba lượt. Chọn DenseNet121 trước khi dùng test. [Báo cáo và đường học](../outputs/training-scene-v1/TRAINING.md).
