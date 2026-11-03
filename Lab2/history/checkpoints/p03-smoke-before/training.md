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
