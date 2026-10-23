# Phân loại ảnh FashionMNIST bằng mạng ANN

## 1. Tổng quan dự án

Dự án thực hiện bài toán phân loại ảnh thời trang FashionMNIST bằng mạng
nơ-ron nhân tạo (Artificial Neural Network - ANN) sử dụng PyTorch.
Notebook xây dựng quy trình từ tải và tiền xử lý dữ liệu, xây dựng mô
hình, huấn luyện, đánh giá đến lưu và tải lại trọng số mô hình.

Mục tiêu là thực hành quy trình Machine Learning cơ bản và theo dõi hiệu
quả mô hình qua Loss, Accuracy, Precision, Recall, F1-score và Confusion
Matrix.

**Phạm vi:** notebook hiện tại sử dụng ANN gồm các lớp Linear và ReLU.
Dự án chưa triển khai CNN hoặc so sánh với các mô hình khác.

## 2. Phát biểu bài toán

### Bài toán

Cho một ảnh thời trang grayscale kích thước 28 × 28 pixel, mô hình dự
đoán ảnh thuộc một trong 10 lớp của FashionMNIST.

-   **Đầu vào:** ảnh grayscale 28 × 28, được chuyển thành tensor; mỗi
    ảnh có 784 giá trị pixel.
-   **Đầu ra:** 10 giá trị đầu ra của mạng, tương ứng 10 lớp. Lớp dự
    đoán là vị trí có giá trị đầu ra lớn nhất (`argmax`).
-   **Dữ liệu:** FashionMNIST do `torchvision.datasets.FashionMNIST` tải
    về, gồm tập train và tập test.

Các lớp nhãn:

1.  T-shirt/top
2.  Trouser
3.  Pullover
4.  Dress
5.  Coat
6.  Sandal
7.  Shirt
8.  Sneaker
9.  Bag
10. Ankle boot

## 3. Các chức năng chính

-   Tải FashionMNIST và chuyển ảnh thành tensor bằng
    `transforms.ToTensor()`.
-   Chuyển ảnh thành bảng 784 cột pixel và lưu tập train/test thành
    `data/train.csv` và `data/test.csv`.
-   Hiển thị 10 ảnh mẫu và tên lớp.
-   Tạo `DataLoader` với batch size 64; xáo trộn dữ liệu train và giữ
    nguyên thứ tự dữ liệu test.
-   Xây dựng mô hình `FashionMNISTModel` bằng PyTorch.
-   Huấn luyện trong 5 epoch bằng `CrossEntropyLoss` và Adam với
    learning rate `0.001`.
-   Theo dõi train/test loss và accuracy theo từng epoch.
-   Tính Accuracy, Macro Precision, Macro Recall, Macro F1-score và các
    chỉ số theo từng lớp.
-   Vẽ Confusion Matrix và hiển thị ảnh cùng nhãn thực tế/dự đoán.
-   Lưu trọng số và tải lại mô hình để kiểm tra.

## 4. Kiến trúc hệ thống

### Cấu trúc mô hình

Mạng ANN có cấu trúc:

`Ảnh 28×28 → Flatten (784) → Linear(784, 128) → ReLU → Linear(128, 64) → ReLU → Linear(64, 10)`

Lớp cuối tạo 10 giá trị đầu ra. Notebook dùng `CrossEntropyLoss` trong
huấn luyện nên không thêm softmax ở cuối mô hình.

### Quy trình xử lý

1.  Tải FashionMNIST cho tập train và test.
2.  Chuyển ảnh sang tensor và tạo `DataLoader`.
3.  Khởi tạo mô hình trên CUDA nếu khả dụng, nếu không thì dùng CPU.
4.  Huấn luyện mô hình trên tập train trong 5 epoch.
5.  Đánh giá sau mỗi epoch và lưu các chỉ số.
6.  Đánh giá cuối cùng, tính các chỉ số phân loại và tạo biểu đồ.
7.  Lưu `state_dict`, tải lại vào một mô hình mới và đánh giá lần nữa.

## 5. Cấu trúc thư mục

Cấu trúc dưới đây thể hiện các thư mục/tệp mà notebook sử dụng hoặc tạo
ra. Các tệp dữ liệu và kết quả chỉ xuất hiện sau khi chạy những cell
tương ứng.

``` text
project/
├── FashionMNIST.ipynb
├── data/
│   ├── train.csv
│   └── test.csv
├── results/
│   ├── loss_curve.png
│   ├── confusion_matrix.png
│   └── predictions.png
└── models/
    └── fashion_mnist_ann.pth
```

  -----------------------------------------------------------------------
  Thư mục/tệp                         Vai trò
  ----------------------------------- -----------------------------------
  `FashionMNIST.ipynb`                Notebook chứa toàn bộ mã tải dữ
                                      liệu, xây dựng, huấn luyện, đánh
                                      giá và lưu/tải mô hình.

  `data/`                             Lưu các tệp CSV được xuất từ tập
                                      FashionMNIST. Dữ liệu huấn luyện
                                      trong notebook vẫn được lấy từ các
                                      dataset của `torchvision`.

  `data/train.csv`                    Tập train dạng bảng, gồm cột
                                      `label` và các cột `pixel0` đến
                                      `pixel783`.

  `data/test.csv`                     Tập test dạng bảng, có cấu trúc
                                      tương tự tập train.

  `results/`                          Lưu các hình kết quả trực quan hóa.

  `results/loss_curve.png`            Biểu đồ training loss và testing
                                      loss theo epoch.

  `results/confusion_matrix.png`      Ma trận nhầm lẫn cho 10 lớp.

  `results/predictions.png`           Ví dụ 10 ảnh test kèm nhãn thực tế
                                      và nhãn dự đoán.

  `models/`                           Thư mục lưu trọng số mô hình.

  `models/fashion_mnist_ann.pth`      Tệp trọng số `state_dict` được lưu
                                      bằng `torch.save`.
  -----------------------------------------------------------------------

## 6. Cài đặt / Chạy chương trình / Kiểm thử

### Yêu cầu môi trường

-   Python 3
-   Jupyter Notebook hoặc Jupyter extension trong VS Code
-   Các thư viện: `torch`, `torchvision`, `matplotlib`, `numpy`,
    `pandas`

### Cài đặt các thư viện

Chạy trong terminal của môi trường Python đang sử dụng:

``` bash
python -m pip install torch torchvision matplotlib numpy pandas jupyter
```

### Các bước chạy chương trình

1.  Mở thư mục dự án trong VS Code.
2.  Mở `FashionMNIST.ipynb` và chọn đúng Python kernel đã cài các thư
    viện.
3.  Chạy lần lượt các cell từ trên xuống dưới.
4.  Ở lần chạy đầu, `torchvision` có thể tải FashionMNIST về thư mục
    `data/`.
5.  Kiểm tra các tệp CSV, biểu đồ và trọng số được tạo sau khi các cell
    tương ứng chạy thành công.

### Kiểm thử chương trình

-   **Dữ liệu:** kiểm tra số lượng mẫu, hình dạng ảnh, kích thước CSV và
    khoảng giá trị pixel được in ra.
-   **Mô hình:** kiểm tra output có 10 giá trị cho mỗi ảnh đầu vào.
-   **Huấn luyện:** xác nhận notebook chạy đủ 5 epoch và in train/test
    loss, accuracy.
-   **Đánh giá:** kiểm tra các chỉ số tổng hợp, chỉ số theo lớp và
    Confusion Matrix.
-   **Lưu/tải:** xác nhận tệp `.pth` được tạo, mô hình mới tải được
    trọng số và các chỉ số sau khi tải tương ứng với kết quả trước khi
    lưu.

**Lưu ý về thư mục `results/`:** notebook gọi `savefig` cho
`loss_curve.png` và `confusion_matrix.png` trước cell tạo thư mục
`results/`. Để tránh lỗi nếu thư mục chưa tồn tại, hãy tạo thư mục trước
khi chạy hai cell này, ví dụ:

``` python
from pathlib import Path
Path("results").mkdir(parents=True, exist_ok=True)
```

## 7. Ví dụ đầu vào -- đầu ra

### Đầu vào

Một batch gồm 64 ảnh có dạng tensor dự kiến:

``` text
Batch image shape: torch.Size([64, 1, 28, 28])
Batch label shape: torch.Size([64])
```

Một ảnh được làm phẳng thành 784 đặc trưng trước khi đi qua các lớp
Linear. Giá trị đầu ra của mô hình có dạng `[batch_size, 10]`.

### Đầu ra

Với một batch gồm 64 ảnh, đầu ra của mô hình có 64 hàng và 10 giá trị
mỗi hàng. Nhãn dự đoán lấy bằng:

``` python
predictions = outputs.argmax(dim=1)
```

Trong quá trình chạy, notebook in loss và accuracy cho từng epoch, sau
đó in Final Test Loss, Final Test Accuracy, Macro Precision, Macro
Recall, Macro F1-score và chỉ số theo từng lớp. Các giá trị số cụ thể
phụ thuộc vào lần chạy thực tế và cần lấy trực tiếp từ output của
notebook.

## 8. Kết quả thực nghiệm

Notebook tạo và hiển thị các kết quả sau:

-   **Training and Testing Loss:** theo dõi loss trên tập train và test
    qua 5 epoch; lưu dự kiến tại `results/loss_curve.png`.
-   **Final Test Loss / Final Test Accuracy:** đánh giá tổng quát trên
    tập test.
-   **Precision, Recall, F1-score:** báo cáo theo từng lớp và giá trị
    macro.
-   **Confusion Matrix:** thể hiện số lượng dự đoán theo từng cặp nhãn
    thực tế và nhãn dự đoán; lưu tại `results/confusion_matrix.png`.
-   **Ảnh dự đoán:** hiển thị 10 ảnh test, nhãn thực tế và nhãn dự đoán;
    màu xanh là dự đoán đúng, màu đỏ là dự đoán sai; lưu tại
    `results/predictions.png`.
-   **Kiểm tra mô hình đã tải:** in loss và accuracy sau khi tải trọng
    số từ `models/fashion_mnist_ann.pth`.

Notebook không cung cấp một bộ chỉ số cố định trong phần mã nguồn; hãy
bổ sung số liệu thực tế từ lần chạy của nhóm vào báo cáo, không tự ước
lượng hoặc tạo số liệu.

## 9. Hạn chế

-   Mô hình hiện tại là ANN dùng các lớp Linear; ảnh được làm phẳng nên
    không khai thác trực tiếp cấu trúc không gian hai chiều như CNN.
-   Notebook huấn luyện trong 5 epoch; số epoch này là cấu hình thực
    nghiệm hiện tại, chưa chứng minh là tối ưu.
-   Notebook chưa có bước dò siêu tham số hoặc so sánh có hệ thống với
    mô hình khác.
-   CSV được xuất để kiểm tra/lưu trữ, nhưng notebook huấn luyện trực
    tiếp từ dataset của `torchvision`, không đọc lại CSV.
-   Biểu đồ loss và confusion matrix có thể không lưu được nếu
    `results/` chưa tồn tại trước khi chạy các cell lưu hình.
-   Hiệu quả mô hình cần được kết luận từ kết quả chạy thực tế, không
    chỉ dựa trên cấu trúc mã.

## 10. Hướng phát triển trong tương lai

-   Thử CNN để khai thác đặc trưng không gian của ảnh.
-   Thử thay đổi số epoch, learning rate, batch size và số nút ở các lớp
    ẩn; ghi lại kết quả để so sánh.
-   Lưu thêm biểu đồ accuracy theo epoch.
-   Tổ chức các phần tải dữ liệu, mô hình, huấn luyện và đánh giá thành
    các module riêng nếu phát triển thành dự án lớn hơn.
-   Thêm kiểm thử tự động cho hình dạng tensor, số lớp đầu ra và tính
    nhất quán của kết quả trước/sau khi tải mô hình.
-   Cải thiện xử lý tạo thư mục kết quả trước khi lưu biểu đồ.

