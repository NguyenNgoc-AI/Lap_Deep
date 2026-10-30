# Phân tích đề Practice 2

## Bài yêu cầu gì?

Đề yêu cầu thực hành sử dụng mạng đã huấn luyện trước, điều chỉnh cho bài toán mới, thử kiến trúc/siêu tham số và theo dõi quá trình học bằng TensorBoard. Đây là bài **transfer learning và fine-tuning cho phân loại ảnh**, không cần tự xây mạng hoặc huấn luyện ImageNet từ đầu.

Dataset người dùng chọn là **Intel Image Classification**, gồm sáu lớp: buildings, forest, glacier, mountain, sea, street. Mỗi ảnh có một nhãn; mô hình xuất sáu logits, dùng CrossEntropyLoss và dự đoán bằng argmax. `seg_pred` không có nhãn nên không dùng để tính accuracy.

## Đối chiếu yêu cầu và cách thực hiện

| Yêu cầu trong hình | Cách thực hiện trong project | Bằng chứng |
|---|---|---|
| Cài PyTorch/torchvision | Môi trường `.venv`, PyTorch XPU trên Intel Arc, CPU đã benchmark dự phòng | `requirements.txt`, `outputs/environment/` |
| Tải pretrained model | VGG11 và DenseNet121, ImageNet1K_V1; dùng API `weights=...` tương ứng thư viện đã cài | `phase_03_models.py`, `outputs/models/weights.json` |
| Xem kiến trúc và tham số | In model, đếm tổng/trainable parameters, liệt kê tham số mở khóa | `outputs/models/*architecture.txt`, `preflight.json` |
| Thay classification layer | Thay linear cuối thành sáu đầu ra | Hàm `build()` trong phase03 |
| Transfer learning | Đóng băng backbone, chỉ học linear cuối; giữ dropout/BatchNorm ở eval | R01–R06, kiểm chứng frozen parameters trong preflight |
| Fine-tune | Từ checkpoint transfer tốt nhất, mở block cuối và linear, LR nhỏ | R07, checkpoint cha và cấu hình trong `identity.json` |
| Chuẩn bị dữ liệu | Audit ảnh/hash/nhãn, tách validation từ train, transforms và DataLoader | `phase_02_data.py`, manifest/audit |
| Đổi hyperparameters | Với mỗi kiến trúc: LR 0.001/B8; LR 0.0003/B8; LR 0.001/B16 | `configs/experiments.json`, R01–R06 |
| Theo dõi TensorBoard | Loss, accuracy và thời gian của train/validation theo epoch | `outputs/experiments/Rxx/tensorboard/` |
| Đánh giá test | Chỉ chạy sau lựa chọn validation; accuracy, macro-F1, từng lớp và confusion matrix | `phase_05_evaluate.py`, `outputs/report/` |

Đường dẫn phase đầy đủ nằm trong `src/phases/`. Notebook `notebooks/main.ipynb` điều phối các phase và trình bày kết quả.

## Thiết kế so sánh

R01–R03 dùng VGG11; R04–R06 dùng DenseNet121. Mỗi run bắt đầu từ cùng weights pretrained, seed 42 và cùng split, chạy 5 epoch. So sánh LR giữ nguyên batch; so sánh batch giữ nguyên LR. Điều này giúp biết yếu tố nào tạo ra chênh lệch quan sát được.

VGG11 dùng các lớp convolution/pooling nối tiếp và phần classifier lớn. DenseNet121 có các dense block nối đặc trưng từ các lớp trước; số tham số ít hơn VGG11. Tốc độ thực trên Intel Arc phải dựa vào số đo của bài, không suy ra chỉ từ số tham số.

R07 tiếp tục từ checkpoint thắng validation, mở block cuối và chạy thêm 3 epoch với LR 0.00001. So sánh R07 với checkpoint cha để quan sát tác dụng của fine-tune; phải nêu rõ R07 được học thêm 3 epoch.

Chọn checkpoint theo validation accuracy cao nhất; hòa thì loss thấp hơn, epoch sớm hơn, run ID nhỏ hơn. Khóa lựa chọn trước khi đánh giá test. Không dùng test để chọn LR, batch, epoch hoặc model cuối.

## Những điểm cần giải thích khi trình bày

- **Pretrained**: dùng tri thức hình ảnh đã học từ ImageNet làm điểm xuất phát.
- **Freeze**: tham số backbone không nhận cập nhật từ optimizer; đầu phân loại mới vẫn học.
- **Fine-tune**: mở thêm block cuối để đặc trưng thích nghi với sáu lớp ảnh phong cảnh.
- **Learning rate**: mức cập nhật trọng số; kết luận tốt/xấu cần dựa trên validation của từng run.
- **Batch size**: số ảnh mỗi bước; thay đổi số bước cập nhật trong một epoch, thời gian và nhu cầu bộ nhớ.
- **Train–validation gap**: train tốt hơn validation có thể phản ánh overfitting; không lấy train accuracy làm kết quả chính.
- **Confusion matrix**: hàng là nhãn thật, cột là dự đoán; xem cặp lớp nào dễ nhầm.
- **Macro-F1**: lấy trung bình F1 của sáu lớp, coi mỗi lớp có trọng lượng bằng nhau.

## Dữ liệu thực tế và giới hạn

Đã kiểm kê 14.034 ảnh train gốc và 3.000 test. Có 13 nhóm ảnh giống byte nhưng khác nhãn. Project cách ly 23 ảnh train thuộc nhóm này; kết hợp lọc trùng/chồng lấn test, tổng loại 28 bản ghi train khỏi manifest. Không sửa hoặc xóa raw/test. Sau tách: 11.208 train và 2.798 validation. Chi tiết tại amendment01 và audit.

Một seed và ngân sách epoch ngắn đáp ứng bài thực hành nhưng chưa đủ để khẳng định kiến trúc nào luôn tốt hơn. SHA256 phát hiện trùng byte, không bảo đảm loại hết ảnh gần giống. Kết quả và nhận xét định lượng chỉ lấy từ báo cáo sau khi các run hoàn tất.
