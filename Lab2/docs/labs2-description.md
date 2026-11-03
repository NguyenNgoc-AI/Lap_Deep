# Lab 2 — Phân loại ảnh phong cảnh bằng VGG11 và DenseNet121

**Ngày 03/11/2026 · Bước Description · Thiết kế thực nghiệm đề xuất để duyệt**

Cho một ảnh phong cảnh RGB, hệ thống dự đoán một nhãn trong sáu lớp **buildings, forest, glacier, mountain, sea, street**. Bài thực hành khảo sát hai câu hỏi. Với cùng dữ liệu và ngân sách huấn luyện, VGG11 và DenseNet121 đạt kết quả validation như thế nào? Với từng kiến trúc, mở khối cuối để fine-tune có cải thiện kết quả so với chỉ học đầu phân loại hay không?

Practice 2 yêu cầu sử dụng các kiến trúc pretrained trong torchvision, khảo sát cấu trúc và tham số, thay lớp phân loại cho bài toán mới, điều chỉnh siêu tham số, theo dõi bằng TensorBoard và đánh giá trên tập test. Các lựa chọn cụ thể về kiến trúc, lịch 5 + 15 epoch và quy tắc chọn checkpoint dưới đây là phương án của Lab 2. [Đề Practice 2, chương 3, trang 23](https://github.com/TiCoder-coder/TOTAL_LABPARACTICE_FOR_DEEP_LEARNING/blob/main/doc_for_agent_study/Chapter%203%20-%20TRAINING%20DEEP%20NEURAL%20NETWORKS%20%281%29.pdf)

## 1. Mô tả bằng 5W1H

| Câu hỏi | Trả lời |
|---|---|
| **What — Làm gì?** | Thực hiện hai run chính, một cho mỗi CNN khởi tạo từ ImageNet. Bàn giao checkpoint của từng run, bảng so sánh và demo dự đoán ảnh. |
| **Why — Vì sao?** | Ảnh băng và ảnh núi có thể có đặc điểm giống nhau. So sánh hai mạng và xem lỗi từng lớp giúp đánh giá chúng học được gì ngoài một con số accuracy tổng hợp. |
| **Who — Ai tham gia?** | Sinh viên chuẩn bị dữ liệu, viết code, chạy và giải thích kết quả. Giảng viên đối chiếu mô tả với hàm thực hiện, log và checkpoint. Người dùng demo cung cấp ảnh cần phân loại. |
| **When — Khi nào?** | Mô tả từng phase trước khi sinh code. Chạy thử trước khi chạy chính thức. Đánh giá validation cuối mỗi epoch. Khóa lựa chọn model và cấu hình trước khi đánh giá test. |
| **Where — Ở đâu?** | Chạy local tại `D:\Lab2` bằng PyTorch và torchvision. Notebook điều phối, TensorBoard theo dõi quá trình học, thư mục `docs/` lưu mô tả và bằng chứng theo phase. |
| **How — Làm thế nào?** | Dùng chung một bản chia dữ liệu. Mỗi mạng lần lượt học classifier rồi fine-tune khối cuối. So sánh thêm hai learning rate từ cùng một checkpoint VGG11 để khảo sát riêng ảnh hưởng của siêu tham số này. |

## 2. Input, output và dữ liệu

Nguồn dữ liệu là Intel Image Classification. `seg_train` cung cấp ảnh có nhãn để lập train/validation, `seg_test` cung cấp ảnh có nhãn để đánh giá và `seg_pred` cung cấp ảnh chưa gán nhãn cho demo. Số ảnh thực dùng ở từng lớp phải lấy từ lần kiểm tra dữ liệu của thiết kế mới. [Nguồn Intel Image Classification](https://www.kaggle.com/datasets/puneet6060/intel-image-classification/data)

| Hoạt động | Input | Output |
|---|---|---|
| Huấn luyện | Batch ảnh RGB 224×224 và nhãn lớp, danh sách mẫu train/validation, ánh xạ nhãn, trọng số ImageNet và cấu hình run | Log theo epoch, dữ liệu TensorBoard, best epoch, `best_val_accuracy`, `best.pt` và `last.pt` |
| Đánh giá | Checkpoint được chọn bằng validation, ảnh test có nhãn, ánh xạ lớp và phép tiền xử lý đánh giá | Dự đoán từng ảnh, bảng metrics, biểu đồ học, confusion matrix và ví dụ dự đoán sai |
| Demo | Một ảnh RGB, checkpoint, ánh xạ lớp và phép tiền xử lý tương ứng | Nhãn dự đoán, điểm softmax của nhãn đó, tên model và epoch của checkpoint |

Đề xuất chia phân tầng phần dữ liệu phát triển theo tỷ lệ 80/20 với seed 42. Trước khi chia, kiểm tra ảnh hỏng, trùng nội dung, mâu thuẫn nhãn và chồng lấn giữa các tập. Ghi quyết định xử lý từng nhóm vào bản kiểm tra dữ liệu. Manifest ghi đường dẫn, nhãn, mã nhận diện nội dung và split. Hai run đọc cùng manifest. Train có thể dùng crop ngẫu nhiên và lật ngang. Validation, test và demo dùng cùng phép biến đổi xác định, với chuẩn hóa phù hợp trọng số ImageNet. [Tài liệu dữ liệu](data.md)

## 3. Kiến trúc và phạm vi học

Cả hai mạng nhận tensor `[B, 3, 224, 224]` và trả `[B, 6]` logits, với B là số ảnh trong batch. Khi đóng băng backbone, ảnh vẫn đi qua các lớp đó để tạo đặc trưng. Optimizer chỉ cập nhật những tham số được mở ở giai đoạn hiện tại.

| Model | Đường đi của ảnh | Giai đoạn 1 học | Giai đoạn 2 học |
|---|---|---|---|
| **VGG11** | 5 khối có 1, 1, 2, 2, 2 lớp convolution. Sau pooling cuối thu được 512×7×7 đặc trưng. Phần Linear có đầu ra lần lượt 4096 → 4096 → 6. | Linear sáu đầu ra mới tại `classifier[6]`. | Linear mới và hai convolution cuối tại `features[16]`, `features[18]`. |
| **DenseNet121** | 4 dense block có 6, 12, 24, 16 dense layer. Mỗi block tái sử dụng đặc trưng từ các lớp trước. Sau global average pooling thu được 1024 đặc trưng cho Linear 1024 → 6. | Linear sáu đầu ra mới tại `classifier`. | Linear mới, `features.denseblock4` và `features.norm5`. |

Đề xuất giữ Dropout của classifier cũ trong VGG ở chế độ đánh giá và giữ cố định thống kê chạy của BatchNorm trong DenseNet. Ở các lớp BatchNorm được mở, hệ số scale và bias vẫn có thể học. Smoke run sẽ kiểm tra cả trọng số lẫn thống kê này. [Sơ đồ từng khối và kích thước tensor](model.md)

## 4. Thiết kế huấn luyện

**Baseline.** Tìm lớp xuất hiện nhiều nhất trên train, luôn dự đoán lớp đó và tính accuracy trên validation. Đây là mốc tối thiểu. Để đo lợi ích của fine-tuning, cần thêm mốc gần hơn là checkpoint tốt nhất sau giai đoạn chỉ học classifier của chính model đó.

**Hai run chính.** Mỗi model dùng Adam, cross-entropy, batch size 8 và seed 42. Một epoch gồm một lượt qua toàn bộ train, sau đó đo trên toàn bộ validation. Loss trung bình được tính theo số ảnh để batch cuối có đúng trọng số. Các epoch được đánh số liên tục trong từng run.

| Giai đoạn | Epoch | LR | Quy tắc thực hiện |
|---|---|---|---|
| Học đầu phân loại | 1–5 | `3e-4` | Chạy đủ 5 epoch. Chọn checkpoint chuyển tiếp theo validation accuracy, nếu hòa xét validation loss rồi epoch sớm hơn. |
| Fine-tuning | 6–20 | `1e-5` | Nạp trọng số từ checkpoint chuyển tiếp, mở đúng các lớp ở mục 3 và khởi tạo Adam mới. Ghi epoch nguồn trước bước cập nhật đầu tiên. |

**Dừng sớm.** Dùng validation loss của checkpoint chuyển tiếp làm mốc đầu giai đoạn 2. Mỗi lần loss giảm ít nhất `1e-4` so với mốc, cập nhật mốc và đặt lại bộ đếm. Dừng khi 3 epoch liên tiếp chưa đạt mức giảm này hoặc khi hoàn tất epoch 20. Mỗi run có tối đa 20 epoch, hai run chính có tối đa 40 epoch tổng cộng.

**Phép thử learning rate.** Chạy thêm một nhánh VGG11 từ đúng checkpoint chuyển tiếp của run chính, chỉ đổi LR fine-tuning từ `1e-5` xuống `3e-6`. Khôi phục cùng điểm xuất phát cho thứ tự lấy mẫu và augmentation. Dùng cùng ngân sách tối đa 15 epoch, chính sách dừng và quy tắc chọn. Báo cáo riêng validation accuracy, loss, best epoch và số epoch thực chạy của hai nhánh. [Lịch huấn luyện chi tiết](training.md)

## 5. Chọn checkpoint và ghi log

`best_val_accuracy` là accuracy validation lớn nhất của **một run, xét cả hai giai đoạn**. Sau mỗi epoch, kể cả epoch kích hoạt dừng, xét lưu `best.pt`. Ưu tiên số ảnh đúng cao hơn trên cùng validation. Khi bằng nhau, ưu tiên loss thấp hơn, sau đó epoch sớm hơn. Ví dụ, nếu epoch 4 và epoch 9 đúng cùng số ảnh, checkpoint có loss thấp hơn thắng. Checkpoint giai đoạn 1 vẫn có thể là best của toàn run.

`best.pt` phục vụ đánh giá và demo. Cần lưu hoặc liên kết trọng số với model, run ID, stage, epoch, metric, ánh xạ lớp và tiền xử lý. `last.pt` lưu trạng thái ở cuối epoch gần nhất để tiếp tục training, gồm trạng thái model, optimizer, bộ đếm dừng sớm và trạng thái sinh số ngẫu nhiên cần thiết.

Mỗi run có cấu hình và nơi lưu log riêng. Log văn bản ghi thời điểm bắt đầu, chuyển giai đoạn, lưu checkpoint, lỗi và lý do kết thúc. Bảng log theo epoch và TensorBoard dùng cùng trục epoch với các trường tối thiểu sau.

```text
run_id, model, stage, epoch, learning_rate, train_samples, val_samples,
train_loss, train_accuracy, val_loss, val_accuracy,
best_val_accuracy, best_epoch, checkpoint_saved, epoch_time
```

## 6. Các phase và bằng chứng nghiệm thu

| Phase | Input → Output | Thuật toán hoặc đoạn code cần giải thích | Kiểm tra |
|---|---|---|---|
| **P01 · Dữ liệu** | Thư mục ảnh → manifest, ánh xạ lớp, thống kê và batch | Đọc nhãn, kiểm tra trùng, chia phân tầng, tiền xử lý và nạp batch | Đối chiếu tổng số mẫu với manifest, kiểm tra chồng lấn và lưu lý do loại mẫu. |
| **P02 · Mô hình** | Trọng số pretrained và batch ảnh → model sáu đầu ra | Hàm thay Linear, đóng/mở tham số và thiết lập mode | In kiến trúc, tên lớp trainable và số tham số. Một batch phải trả logits hữu hạn dạng `[B, 6]`. |
| **P03 · Huấn luyện** | Model và batch train/validation → lịch sử epoch và checkpoint | Forward tạo logits, cross-entropy đo sai số, backpropagation tính gradient, Adam cập nhật tham số | Dùng một bước train để kiểm tra classifier được cập nhật và phần khóa giữ nguyên. Đối chiếu best epoch trong log với checkpoint. |
| **P04 · Đánh giá** | Checkpoint và ảnh test có nhãn → bảng so sánh và phân tích lỗi | Nạp lại đúng model, dùng lớp có logit cao nhất để lập bảng dự đoán và confusion matrix | Tổng các ô bằng số ảnh test. Tổng đường chéo chia tổng số ảnh bằng accuracy báo cáo. [Tiêu chí đánh giá](evaluation.md) |
| **P05 · Demo** | Ảnh mới và checkpoint → nhãn, điểm và thông tin model | Áp dụng tiền xử lý đánh giá, chạy inference và tra tên lớp theo ánh xạ đã lưu | Chỉ số dự đoán khớp nhãn hiển thị. Ví dụ demo ghi rõ ảnh, run và epoch. [Mô tả demo](demo.md) |

Khi triển khai, tài liệu của từng phase ghi **đường dẫn file, tên hàm thực tế, đoạn code quyết định hành vi, cách chạy và log liên quan**. Ví dụ ở P03, người chấm phải lần được từ dòng log “lưu best” đến hàm so sánh metric, epoch thắng và đúng file checkpoint.

## 7. Quy trình thực hiện và đánh giá cuối

| Bước | Sản phẩm hoặc điều kiện chuyển bước |
|---|---|
| **Description** | Chốt input/output, thiết kế run, tiêu chí đạt và cách kiểm tra cho từng phase. |
| **Generate** | Viết hàm/module theo mô tả, ghi nơi triển khai và giải thích thuật toán. |
| **Smoke run** | Chạy ít ảnh hoặc vài batch để kiểm tra shape, gradient, freeze, chuyển stage và lưu/nạp checkpoint. Tách log và checkpoint chạy thử khỏi normal run. |
| **Normal run** | Sau khi smoke run đạt, chạy cấu hình đầy đủ, lưu log thật, metrics và checkpoint của từng run. |
| **Check against description** | Đánh dấu PASS/FAIL theo từng tiêu chí, dẫn tới bằng chứng. Nạp lại `best.pt` để đối chiếu số ảnh validation dự đoán đúng với log trước khi đánh giá test. [Theo dõi tiến độ](plan-progress.md) |

Báo cáo cuối so sánh hai model theo cùng split, quy tắc checkpoint và ngân sách tối đa. Ghi số epoch thực chạy, thời gian, validation accuracy/loss và kết quả test của checkpoint đã khóa. Với mỗi lớp, báo cáo precision, recall, F1 và số ảnh thật. Đọc confusion matrix với nhãn thật theo hàng và nhãn dự đoán theo cột. Phân tích overfitting bằng diễn biến đồng thời của train/validation qua nhiều epoch. Một dao động đơn lẻ trên biểu đồ chưa đủ để kết luận.

Demo sử dụng checkpoint đã chọn và ghi rõ run, stage, epoch. Diễn giải kết quả trong phạm vi một seed. Tập test đã được xem trong lần làm Lab 2 trước, nên báo cáo phải ghi lịch sử này khi nhận xét khả năng tổng quát hóa.

**Trạng thái bàn giao.** Bản Description đã đủ để rà soát thiết kế. Trước Generate cần xác nhận quy tắc chia và xử lý ảnh trùng, phạm vi mở khóa, lịch huấn luyện, phép thử LR và quy tắc checkpoint. Số lượng mẫu sau kiểm tra, log, biểu đồ và kết quả sẽ được điền từ lần chạy thực tế.
