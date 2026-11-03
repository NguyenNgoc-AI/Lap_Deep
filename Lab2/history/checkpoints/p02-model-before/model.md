# Mô hình

**P02 · Thiết kế đề xuất cho hai run chính.** Mỗi mạng khởi tạo từ trọng số ImageNet của torchvision. Với một batch B ảnh RGB đã tiền xử lý, ví dụ `[B, 3, 224, 224]`, mỗi mạng trả `[B, 6]` logits theo cùng ánh xạ nhãn. Backbone là phần biến ảnh thành đặc trưng. Classifier dùng các đặc trưng đó để tính điểm cho từng lớp.

## Ảnh đi qua những lớp nào?

| Model | Luồng trích đặc trưng | Đầu phân loại cho Lab 2 |
|---|---|---|
| VGG11 (bản thường) | 5 khối lần lượt có **1, 1, 2, 2, 2** lớp convolution 3×3. Số kênh ra theo khối là **64, 128, 256, 512, 512**. Sau mỗi conv có ReLU và cuối mỗi khối có max pooling. Với ảnh 224×224, kích thước sau năm lần pooling lần lượt là 112, 56, 28, 14 và 7. | Từ đặc trưng 512×7×7, làm phẳng rồi qua ba lớp Linear có kích thước đầu ra **4096 → 4096 → 6**. Thay `classifier[6]` bằng `Linear(4096, 6)`. Tên VGG11 đếm **8 convolution + 3 Linear**. |
| DenseNet121 | Sau convolution và pooling đầu mạng là 4 dense block gồm **6, 12, 24, 16** dense layer. Mỗi dense layer nhận các đặc trưng trước đó trong cùng block, dùng một conv 1×1 và một conv 3×3. Giữa bốn block có ba transition để giảm kích thước. | Sau block cuối và `norm5`, mạng dùng ReLU và global average pooling để lấy vector **1024** đặc trưng. Thay `classifier` bằng `Linear(1024, 6)`. Số **121** gồm 1 conv đầu, 116 conv trong 58 dense layer, 3 conv transition và 1 Linear. |

## Sơ đồ kiến trúc cho ảnh RGB 224 × 224

Kích thước bên phải ghi theo thứ tự **kênh × cao × rộng** của một ảnh. Với batch B ảnh, thêm chiều B ở đầu. Ký hiệu **[G2]** đánh dấu phần chỉ mở ở giai đoạn fine-tuning. **[G1+G2]** đánh dấu lớp mới học ở cả hai giai đoạn. Các trọng số pretrained ở những phần còn lại được giữ cố định.

### VGG11

```text
Ảnh RGB                                                 3 × 224 × 224
  ↓ Khối 1 · (Conv 3×3 → ReLU) ×1 → MaxPool           64 × 112 × 112
  ↓ Khối 2 · (Conv 3×3 → ReLU) ×1 → MaxPool          128 ×  56 × 56
  ↓ Khối 3 · (Conv 3×3 → ReLU) ×2 → MaxPool          256 ×  28 × 28
  ↓ Khối 4 · (Conv 3×3 → ReLU) ×2 → MaxPool          512 ×  14 × 14
  ↓ Khối 5 · (Conv 3×3 → ReLU) ×2 → MaxPool  [G2]    512 ×   7 × 7
  ↓ AdaptiveAvgPool(7×7) → Flatten                         25.088
  ↓ Linear → ReLU → Dropout                                 4.096
  ↓ Linear → ReLU → Dropout                                 4.096
  ↓ Linear(4096, 6) [G1+G2]                              6 logits
```

Mỗi MaxPool dùng cửa sổ 2×2 với stride 2. Hai conv của khối 5 là `features[16]` và `features[18]`; Linear mới là `classifier[6]`.

### DenseNet121

```text
Ảnh RGB                                                 3 × 224 × 224
  ↓ Conv 7×7, stride 2 → BN → ReLU                     64 × 112 × 112
  ↓ MaxPool 3×3, stride 2                              64 ×  56 × 56
  ↓ denseblock1 ·  6 dense layer                      256 ×  56 × 56
  ↓ transition1                                       128 ×  28 × 28
  ↓ denseblock2 · 12 dense layer                      512 ×  28 × 28
  ↓ transition2                                       256 ×  14 × 14
  ↓ denseblock3 · 24 dense layer                    1.024 ×  14 × 14
  ↓ transition3                                       512 ×   7 × 7
  ↓ denseblock4 · 16 dense layer [G2]                1.024 ×   7 × 7
  ↓ norm5 [G2] → ReLU                                1.024 ×   7 × 7
  ↓ Global average pooling → Flatten                        1.024
  ↓ Linear(1024, 6) [G1+G2]                              6 logits
```

Trong một dense layer, các đặc trưng đầu vào đi qua BN → ReLU → Conv 1×1 → BN → ReLU → Conv 3×3 để tạo **32 kênh mới**. Mạng ghép chúng với các kênh đã có. Chẳng hạn khối 4 nhận 512 kênh và trả 512 + 16 × 32 = 1.024 kênh. Mỗi transition dùng BN → ReLU → Conv 1×1 để giảm một nửa số kênh, sau đó dùng average pooling 2×2 để giảm một nửa chiều cao và chiều rộng.

## Freeze backbone như thế nào?

Khi freeze, ảnh vẫn đi qua các lớp để tạo đặc trưng. Tham số đã khóa có `requires_grad=False`; optimizer chỉ nhận tham số của các lớp được học.

| Giai đoạn | VGG11 | DenseNet121 |
|---|---|---|
| 1 · Học đầu phân loại | Khóa toàn bộ trọng số pretrained, kể cả hai Linear 4096. Chỉ học Linear mới tại `classifier[6]`. | Khóa toàn bộ `features`. Chỉ học Linear mới tại `classifier`. |
| 2 · Fine-tune khối cuối | Tiếp tục học `classifier[6]` và mở khối 5 (`features[16:]`). Trong khối này hai conv có trọng số là `features[16]` và `features[18]`. Bốn khối đầu và hai Linear 4096 vẫn khóa. | Tiếp tục học `classifier` và mở `features.denseblock4` cùng `features.norm5`. Phần đầu mạng, ba dense block đầu và toàn bộ transition vẫn khóa. |

Giai đoạn 1 cho đầu ra mới học cách phân loại sáu lớp từ đặc trưng có sẵn. Giai đoạn 2 cho khối cuối điều chỉnh đặc trưng theo ảnh phong cảnh với learning rate nhỏ hơn. Khi chuyển giai đoạn, optimizer phải bao gồm các tham số vừa mở.

**Chính sách mode đề xuất.** Giữ Dropout trong phần classifier cũ của VGG11 ở chế độ đánh giá để đặc trưng qua hai Linear cố định không bị bỏ ngẫu nhiên. Với DenseNet121, giữ thống kê chạy của BatchNorm cố định trong cả hai giai đoạn. Ở giai đoạn 2, hệ số scale và bias của BatchNorm trong khối mở vẫn có thể học. Khi validation, dùng `eval()` và tắt tính gradient.

**Đối chiếu trong smoke run.** In tên và số tham số trainable của từng giai đoạn. Với một bước cập nhật trên batch có nhãn, kiểm tra logits có sáu cột, classifier mới có gradient và thay đổi trọng số, phần đóng băng giữ nguyên. Ở giai đoạn 2 kiểm tra thêm gradient ở khối cuối và thống kê BatchNorm cố định. Các kiểm tra này hiện là tiêu chí cho bước triển khai.

Nguồn kiến trúc: [VGG trong torchvision](https://github.com/pytorch/vision/blob/main/torchvision/models/vgg.py) và [DenseNet trong torchvision](https://github.com/pytorch/vision/blob/main/torchvision/models/densenet.py).
