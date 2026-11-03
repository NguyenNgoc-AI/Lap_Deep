# Lab 2 — Phân loại ảnh phong cảnh bằng mạng neural pretrained

**Bản nháp để thảo luận · 03/11/2026 · Bước Description**

## Bài toán

Cho một ảnh RGB, hệ thống dự đoán một trong sáu lớp của bộ Intel Image Classification: buildings, forest, glacier, mountain, sea hoặc street. Câu hỏi thực nghiệm là khi dùng cùng dữ liệu và ngân sách huấn luyện, VGG và DenseNet tận dụng đặc trưng đã học trên ImageNet như thế nào để phân loại các cảnh này? Sản phẩm cuối gồm hai run có thể đối chiếu, checkpoint đã chọn của từng run và ví dụ nạp lại checkpoint để dự đoán một ảnh. [Nguồn dữ liệu](https://www.kaggle.com/datasets/puneet6060/intel-image-classification/data)

Practice 2 yêu cầu khảo sát kiến trúc pretrained trong torchvision, thay lớp phân loại, điều chỉnh siêu tham số và theo dõi quá trình học bằng TensorBoard. Báo cáo phải chỉ ra mối liên hệ giữa thuật toán, đoạn code thực hiện và kết quả quan sát được trong log. [Đề bài, chương 3, trang 23](https://github.com/TiCoder-coder/TOTAL_LABPARACTICE_FOR_DEEP_LEARNING/blob/main/doc_for_agent_study/Chapter%203%20-%20TRAINING%20DEEP%20NEURAL%20NETWORKS%20%281%29.pdf)

## 5W1H của Lab 2

| Câu hỏi | Trả lời cho bài thực hành |
|---|---|
| **What — Làm gì?** | Xây dựng và so sánh hai mô hình pretrained cho bài toán phân loại ảnh phong cảnh. Mỗi ảnh nhận đúng một nhãn trong sáu lớp. |
| **Why — Vì sao?** | Dùng đặc trưng đã học từ ImageNet làm điểm xuất phát. Đo kết quả khi chỉ học đầu phân loại, sau đó đo lại khi mở một phần backbone để biết fine-tuning ảnh hưởng thế nào đến accuracy và loss. |
| **Who — Ai tham gia?** | Sinh viên chuẩn bị dữ liệu, triển khai, chạy và giải thích kết quả. Giảng viên đối chiếu mô tả với code, log và checkpoint. Người chạy demo cung cấp ảnh và xem dự đoán. |
| **When — Khi nào?** | Trước khi viết code, chốt đầu vào, đầu ra và tiêu chí đạt. Sau khi sinh code, smoke run kiểm tra đường chạy. Khi đạt mới chạy normal run. Cuối mỗi epoch đánh giá validation. Sau khi khóa checkpoint mới đánh giá test và chạy demo. |
| **Where — Ở đâu?** | Bài chạy trên máy local trong `D:\Lab2` với PyTorch và torchvision. Notebook điều phối các phase, TensorBoard hiển thị diễn biến huấn luyện và thư mục `docs/` giải thích kết quả. |
| **How — Làm thế nào?** | Chuẩn bị cùng bộ ảnh và cách chia tập cho hai model. Đề xuất dùng VGG11 và DenseNet121, thay classifier bằng sáu đầu ra, huấn luyện theo hai giai đoạn rồi chọn checkpoint bằng validation. Dùng log để kiểm tra lại quyết định chọn. |

## Input và output của toàn bài

| Hoạt động | Input — cần có trước khi chạy | Output — cần thu sau khi chạy |
|---|---|---|
| Huấn luyện và chọn checkpoint | Ảnh RGB có nhãn, danh sách mẫu train/validation, ánh xạ sáu lớp, trọng số ImageNet và cấu hình của từng run. | Log theo epoch và dữ liệu TensorBoard. Mỗi run có best epoch, giá trị validation tại epoch đó, `best.pt` để đánh giá và `last.pt` để tiếp tục huấn luyện. |
| Đánh giá | Checkpoint đã chọn, ảnh test có nhãn thật, ánh xạ lớp và phép tiền xử lý đánh giá. | Dự đoán từng ảnh, bảng metrics, confusion matrix và phân tích lỗi gắn với đúng run và checkpoint. |
| Demo | Một ảnh RGB do người dùng cung cấp, checkpoint, ánh xạ lớp và phép tiền xử lý tương ứng. Ảnh demo có thể chưa có nhãn. | Tên lớp dự đoán, điểm softmax tương ứng và thông tin model/epoch tạo ra dự đoán. |

## Thiết kế thực nghiệm đề xuất

- **Mốc đối chiếu.** Xác định lớp phổ biến nhất trên train và tính accuracy khi luôn dự đoán lớp đó trên validation. Giai đoạn chỉ học đầu phân loại của mỗi CNN cung cấp thêm một mốc để đo tác dụng của fine-tuning.
- **Hai run chính.** Đề xuất một run VGG11 và một run DenseNet121. Mỗi run bắt đầu từ trọng số ImageNet, thay đầu ra bằng sáu logits, rồi huấn luyện qua hai giai đoạn trong cùng một lịch sử epoch. Giai đoạn đầu đóng băng backbone và học classifier mới. Giai đoạn sau mở một phần backbone, dùng learning rate nhỏ hơn và ghi rõ checkpoint chuyển tiếp. VGG xếp các lớp tích chập nối tiếp, còn DenseNet nối các bản đồ đặc trưng bên trong dense block. Khi khảo sát, phải xác định trên model thực lớp nào được mở và bao nhiêu tham số được học.
- **So sánh công bằng.** Dùng cùng manifest, seed, cách tiền xử lý, tiêu chí chọn checkpoint và ngân sách epoch tối đa. Báo cáo cả số epoch thực chạy và thời gian của từng run. Một seed chỉ cho phép mô tả kết quả của lần chạy đó.
- **Điều chỉnh siêu tham số.** Đề xuất một phép so sánh phụ trên một kiến trúc, chỉ thay learning rate của giai đoạn fine-tuning. Hai nhánh xuất phát từ cùng checkpoint, dùng cùng split, batch và ngân sách. Ghi riêng phép so sánh này để người đọc phân biệt tác dụng của learning rate với khác biệt giữa hai kiến trúc.

## Các phase và bằng chứng cần thu

| Phase | Input | Cách xử lý | Output và cách kiểm tra |
|---|---|---|---|
| P01 · Dữ liệu | Ảnh gốc, nhãn thư mục và tập test do bộ dữ liệu cung cấp. | Kiểm tra ảnh lỗi, trùng hoặc mâu thuẫn nhãn. Chia phần phát triển theo lớp. Áp dụng augmentation cho train và tiền xử lý xác định cho validation/test. | Manifest ghi đường dẫn, nhãn và split của từng ảnh. Đối chiếu số mẫu từng lớp với manifest, ghi lý do loại mẫu và lưu ánh xạ lớp cho các phase sau. [Chi tiết](data.md) |
| P02 · Mô hình | Kiến trúc, trọng số pretrained, số lớp từ P01 và một batch ảnh để kiểm tra. | Khảo sát mạng, thay classifier và xác định tham số được học trong mỗi giai đoạn. | Model sẵn sàng cho P03, bản in kiến trúc và danh sách tham số trainable. Với batch B ảnh, kiểm tra đầu ra là logits có shape `[B, 6]`. [Chi tiết](model.md) |
| P03 · Huấn luyện | Model từ P02, batch train/validation từ P01 và cấu hình run. | Tính cross-entropy, dùng backpropagation tính gradient và optimizer cập nhật trọng số. Tính loss và accuracy trên toàn bộ validation cuối mỗi epoch. | Log, TensorBoard, best epoch, `best.pt` và `last.pt`. Đối chiếu checkpoint được chọn với dòng log của epoch tương ứng. [Chi tiết](training.md) |
| P04 · Đánh giá | `best.pt` từ P03, ảnh test có nhãn, ánh xạ lớp và phép tiền xử lý từ P01. | Nạp checkpoint đã khóa, dự đoán trên test, đối chiếu nhãn dự đoán với nhãn thật. | Accuracy, macro-F1, precision/recall/F1 và số mẫu từng lớp, confusion matrix. Tổng số phần tử trong ma trận phải bằng số ảnh được đánh giá. Ghi rõ test đã từng được xem trong lần làm trước. [Chi tiết](evaluation.md) |
| P05 · Demo | Ảnh RGB mới, `best.pt`, ánh xạ lớp và phép tiền xử lý dùng khi đánh giá. | Chạy inference, lấy lớp có điểm cao nhất và tra tên lớp theo ánh xạ đã lưu. | Hiển thị ảnh, tên lớp, điểm softmax và run/epoch của checkpoint. Kiểm tra tên lớp khớp chỉ số dự đoán. [Chi tiết](demo.md) |

Ở từng phase, tài liệu sẽ ghi tên file/hàm thực tế, trích đoạn code quyết định hành vi, giải thích thuật toán và dẫn tới log của chính lần chạy đó.

## Quy trình kiểm chứng

| Bước | Việc thực hiện và điều kiện chuyển bước |
|---|---|
| Description | Chốt mục tiêu, input/output, thuật toán và tiêu chí đạt của phase. |
| Generate | Viết code theo mô tả và xác định hàm chịu trách nhiệm cho từng đầu ra. |
| Smoke run | Chạy trên ít ảnh hoặc vài batch. Với training, kiểm tra sáu logits, loss hữu hạn, tham số được phép học có cập nhật và checkpoint nạp lại được. Lưu log riêng cho lần chạy thử. |
| Normal run | Khi smoke run đạt, chạy trên đủ dữ liệu theo cấu hình đã chốt. Lưu số mẫu, thời gian, metrics, checkpoint và lý do dừng. |
| Check against description | Đối chiếu từng tiêu chí với file/hàm, log và kết quả của normal run. Ghi PASS hoặc FAIL cùng bằng chứng. Theo dõi tại [plan-progress.md](plan-progress.md). |

## Quy tắc chọn checkpoint và log đề xuất

Đề xuất định nghĩa `best_val_accuracy` là validation accuracy cao nhất qua **cả hai giai đoạn** của một run. Khi bằng accuracy, ưu tiên validation loss thấp hơn, rồi epoch sớm hơn. `best.pt` lưu trọng số tại epoch thắng theo quy tắc đó. `last.pt` lưu trạng thái ở epoch cuối đã chạy, gồm thông tin cần thiết để tiếp tục training. Nếu dùng early stopping, phải chốt riêng chỉ số theo dõi và số epoch chờ trước normal run.

Mỗi dòng log epoch cần có run ID, model, stage, epoch, learning rate, train/validation loss và accuracy, số mẫu, thời gian, best epoch và sự kiện lưu checkpoint. Tệp cấu hình ghi seed, batch, optimizer, split và chính sách freeze/unfreeze. Cuối run ghi lý do dừng. TensorBoard và bảng log phải dùng cùng số epoch và giá trị metric.

Một kiểm tra cụ thể cho báo cáo là tìm epoch tốt nhất từ bảng log, đối chiếu với epoch ghi trong `best.pt`, rồi nạp lại checkpoint để tái lập validation accuracy. Nhờ vậy giáo viên có thể kiểm tra lựa chọn model trực tiếp từ kết quả chạy.

## Các quyết định cần chốt trước Generate

1. Xác nhận hai kiến trúc, các lớp mở khóa và checkpoint dùng để chuyển giai đoạn.
2. Chốt ngân sách epoch của từng giai đoạn, batch size, optimizer, learning rate và điều kiện dừng phù hợp với máy local.
3. Chốt cách chia dữ liệu, seed, quy tắc xử lý ảnh trùng, metric chính và quy tắc hòa điểm.
4. Chọn kiến trúc và hai giá trị learning rate cho phép so sánh phụ, ghi trước tiêu chí đánh giá.

Số liệu và biểu đồ sẽ lấy từ normal run của thiết kế được duyệt. Hiện các phase đang ở bước mô tả.
