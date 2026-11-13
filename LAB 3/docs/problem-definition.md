# Problem Definition — Lab 3

## 1. Bối cảnh

Review phim, bình luận sản phẩm hay bài đăng mạng xã hội có số lượng lớn, không thể đọc tay hết. Phân tích cảm xúc (sentiment analysis) tự động cho biết một câu là khen hay chê, giúp tổng hợp ý kiến nhanh. Bài thực hành dùng Hugging Face để giải bài toán này theo hai cách: dùng ngay model có sẵn (Exercise 1) và tự fine-tune model cho dữ liệu mới (Exercise 2).

## 2. Phát biểu bài toán

**Phân loại cảm xúc nhị phân cho câu tiếng Anh.**

- Đầu vào: một câu tiếng Anh `x` (chuỗi ký tự, thường dưới 60 từ).
- Đầu ra: nhãn `y ∈ {0 = NEGATIVE, 1 = POSITIVE}` và độ tin cậy `p(y | x) ∈ [0, 1]`.
- Cần tìm hàm `f(x) = argmax p(y | x)` sao cho dự đoán đúng nhãn của các câu chưa gặp.

| | Exercise 1 | Exercise 2 |
|---|---|---|
| Loại bài toán | Suy luận (inference) | Học có giám sát: fine-tune model đã huấn luyện sẵn |
| Dữ liệu có nhãn | Không dùng | `rotten_tomatoes`: 8.530 câu train, 1.066 validation, 1.066 test |
| Model | Đã fine-tune sẵn trên SST-2, dùng nguyên | DistilBERT gốc + lớp phân loại 2 nhãn mới, cập nhật toàn bộ tham số |
| Mục tiêu học | – | Cực tiểu hóa cross-entropy giữa `p(y | x)` và nhãn thật trên tập train |

## 3. Mục tiêu

1. **Mục tiêu học tập (theo đề):** thực hiện đủ 4 yêu cầu Exercise 1 và 7 yêu cầu Exercise 2 bằng `transformers`, `datasets`, `evaluate`, `Trainer` — đối chiếu ở [labs3-description.md](labs3-description.md).
2. **Mục tiêu mô hình:** model sau fine-tune phải tốt hơn rõ rệt model chưa fine-tune trên cùng tập test.
3. **Mục tiêu phân tích:** giải thích được kết quả — lỗi theo lớp, overfitting, các loại câu khó (trung tính, phủ định, mỉa mai).

Nhóm không đặt trước một ngưỡng accuracy cụ thể; tiêu chí là vượt rõ baseline và giải thích được.

## 4. Tiêu chí đánh giá

| Chỉ số | Vì sao dùng |
|---|---|
| **Accuracy** (chính) | Hai lớp cân bằng tuyệt đối (533/533 câu mỗi lớp ở tập test) nên accuracy phản ánh đúng chất lượng |
| F1, precision, recall (lớp POSITIVE) | Phát hiện model nghiêng về một lớp, điều accuracy không cho thấy |
| Confusion matrix | Xem lỗi rơi vào chiều nào |
| Validation loss theo epoch | Phát hiện overfitting, chọn số epoch |
| Baseline | DistilBERT với lớp phân loại chưa huấn luyện, chấm trên cùng tập test |

**Giao thức:** train trên `train`; theo dõi và chọn model trên `validation`; chấm `test` **một lần** sau khi đã chọn xong. Không dùng `test` để chỉnh siêu tham số.

**Kết quả đạt được** (chi tiết: [evaluation.md](evaluation.md)): test accuracy 84.62% so với 42.87% của baseline.

## 5. Giả định

- Câu là tiếng Anh, ngắn (rotten_tomatoes: trung bình 21 từ, dài nhất 59 từ).
- Nhãn trong bộ dữ liệu là đúng; nhóm không kiểm tra lại nhãn.
- Mỗi câu chỉ mang một cảm xúc chủ đạo (khen hoặc chê).
- Phân bố câu khi dùng thật tương tự review phim trong dữ liệu.

## 6. Ràng buộc

| Ràng buộc | Ảnh hưởng tới lời giải |
|---|---|
| Đề yêu cầu dùng Hugging Face `transformers`, `datasets`, `evaluate`, `Trainer` | Không tự viết vòng lặp huấn luyện |
| Phần cứng: laptop Windows, GPU RTX 3050 **6 GB** VRAM | Chọn model nhỏ (DistilBERT), batch 16, fp16 |
| Thời gian thực hành ngắn | Bộ dữ liệu nhỏ, 3 epoch (~2 phút trên GPU) |
| Repo GitHub giới hạn 100 MB/file | Không lưu model (~270 MB) lên repo; tạo lại bằng script |
| Mạng có thể chập chờn | Dữ liệu xuất ra CSV, chỉ số `evaluate` dùng bản lưu trên máy |

## 7. Phạm vi

**Trong phạm vi:** phân loại 2 nhãn câu tiếng Anh; một model (DistilBERT); một bộ dữ liệu; đánh giá offline trên tập test; demo dòng lệnh.

**Ngoài phạm vi:** nhãn trung tính hay nhiều mức cảm xúc; tiếng Việt hay đa ngôn ngữ; nhận diện mỉa mai; so sánh nhiều kiến trúc hay dò siêu tham số; triển khai thành dịch vụ web/API.

Thiết kế lời giải: [design.md](design.md).
