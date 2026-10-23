# Tài liệu khai báo việc sử dụng AI

## 1. Công cụ AI đã sử dụng

-   **ChatGPT:** có thể được sử dụng để hỗ trợ giải thích mã nguồn, tổ
    chức nội dung tài liệu, gợi ý cách kiểm tra lỗi và diễn giải các
    khái niệm Machine Learning.
-   **Claude** có thể được sử dụng để hỗ trợ giải thích mã nguồn, tổ
    chức nội dung tài liệu, gợi ý cách kiểm tra lỗi và diễn giải các
    khái niệm Machine Learning.
-   **Jupyter Notebook / VS Code:** môi trường chạy và kiểm tra
    notebook; đây là công cụ phát triển, không phải công cụ AI.

## 2. Mục đích sử dụng AI

AI được sử dụng như công cụ hỗ trợ trong các công việc sau, nếu phù hợp
với quá trình thực hiện thực tế:

-   Giải thích các khái niệm như FashionMNIST, tensor, ANN, forward
    pass, backpropagation, loss, accuracy và các chỉ số đánh giá.
-   Hỗ trợ đọc hiểu cấu trúc code PyTorch và ý nghĩa của các hàm/lớp
    được sử dụng.
-   Gợi ý cách tìm nguyên nhân lỗi khi chạy notebook, đặc biệt là lỗi
    đường dẫn hoặc thư mục lưu kết quả.
-   Hỗ trợ rà soát cách trình bày README và tài liệu mô tả quy trình.
-   Gợi ý cách kiểm tra tính nhất quán giữa kết quả trước và sau khi
    lưu/tải mô hình.

AI không được xem là nguồn xác nhận kết quả thực nghiệm. Các chỉ số phải
lấy từ output thật của notebook.

## 3. Đóng góp của sinh viên

Các thành viên cần mô tả chính xác phần việc do mình trực tiếp thực
hiện. Dựa trên notebook, các hạng mục công việc có thể được phân chia và
xác nhận gồm:

-   Tổ chức và chạy notebook theo 5 bước: tải/tiền xử lý dữ liệu, xây
    dựng ANN, huấn luyện, đánh giá và lưu/tải mô hình.
-   Đọc hiểu và kiểm tra các lớp, hàm và tham số trong mã nguồn.
-   Chạy thử notebook, kiểm tra output và xử lý lỗi trong môi trường
    thực tế.
-   Đọc các chỉ số và biểu đồ để đưa ra nhận xét dựa trên kết quả.
-   Hoàn thiện README, AI_USAGE và báo cáo thực nghiệm.

## 4. Các thành phần có sự hỗ trợ đáng kể từ AI

Nếu AI có hỗ trợ đáng kể, nhóm nên ghi rõ thành phần được hỗ trợ và mức
độ chỉnh sửa. Những phần trong notebook cần khai báo dựa trên lịch sử
làm việc thực tế có thể gồm:

-   Giải thích hoặc gợi ý cho phần tiền xử lý dữ liệu và tạo
    `DataLoader`.
-   Giải thích kiến trúc `FashionMNISTModel`, hàm huấn luyện
    `train_one_epoch()` và hàm đánh giá `evaluate()`.
-   Gợi ý hoặc rà soát cách tính Accuracy, Precision, Recall, F1-score
    và Confusion Matrix.
-   Hỗ trợ viết hoặc chỉnh sửa phần mô tả quy trình trong `README.md` và
    `AI_USAGE.md`.

## 5. Mục đích của các nhóm câu lệnh (prompt)

Bảng dưới đây là mẫu ghi lại **mục đích** của từng nhóm prompt. Hãy sửa
hoặc bổ sung theo prompt thực sự đã dùng; không coi đây là bản ghi
nguyên văn lịch sử trò chuyện.

  -----------------------------------------------------------------------
  Nhóm prompt                         Mục đích
  ----------------------------------- -----------------------------------
  Hỏi giải thích kiến thức            Hiểu FashionMNIST, tensor, ANN,
                                      loss, optimizer và các chỉ số đánh
                                      giá.

  Hỏi về code                         Hiểu cách hoạt động của từng cell
                                      và luồng dữ liệu qua mô hình.

  Hỏi sửa lỗi                         Tìm nguyên nhân lỗi khi tải dữ
                                      liệu, chạy cell hoặc lưu tệp.

  Hỏi đánh giá kết quả                Hiểu output, biểu đồ loss,
                                      confusion matrix và chỉ số theo
                                      lớp.

  Hỏi viết tài liệu                   Tổ chức nội dung README/AI_USAGE rõ
                                      ràng, nhất quán với notebook.
  -----------------------------------------------------------------------

## 6. Những chỉnh sửa của sinh viên

Sau khi nhận gợi ý từ AI, sinh viên cần tự kiểm tra và chỉnh sửa để nội
dung phù hợp với notebook và kết quả thực tế. Các hạng mục nên ghi nhận
nếu nhóm đã thực hiện gồm:

-   Đối chiếu code được gợi ý với các cell hiện có và sửa những phần
    không phù hợp.
-   Kiểm tra kích thước tensor, số lớp đầu ra, tham số huấn luyện và
    công thức tính chỉ số.
-   Chạy lại các cell để xác nhận chương trình hoạt động trong môi
    trường của nhóm.
-   Sửa nội dung tài liệu để phản ánh đúng tên file, đường dẫn, cấu trúc
    mô hình và số epoch.
-   Thay mọi số liệu minh họa bằng số liệu thực tế thu được khi chạy
    notebook.

## 7. Phương pháp kiểm chứng

Nhóm có thể kiểm chứng kết quả bằng các bước sau và ghi rõ bước nào đã
thực hiện:

1.  **Kiểm tra dữ liệu:** chạy các cell tải FashionMNIST, kiểm tra số
    lượng mẫu, hình dạng ảnh, kích thước CSV và khoảng giá trị pixel.
2.  **Kiểm tra mô hình:** xác nhận ảnh đầu vào có kích thước 28 × 28 và
    đầu ra có 10 giá trị cho mỗi ảnh.
3.  **Kiểm tra huấn luyện:** chạy đủ 5 epoch; xem train/test loss và
    accuracy được in ở mỗi epoch.
4.  **Kiểm tra chỉ số:** đối chiếu Accuracy, Macro Precision, Macro
    Recall, Macro F1-score và các chỉ số theo lớp với dữ liệu nhãn thật
    và nhãn dự đoán.
5.  **Kiểm tra trực quan:** xem biểu đồ loss, Confusion Matrix và các
    ảnh dự đoán; không kết luận chỉ từ một chỉ số riêng lẻ.
6.  **Kiểm tra lưu/tải:** xác nhận tệp `models/fashion_mnist_ann.pth`
    tồn tại, tải trọng số vào mô hình mới và so sánh loss/accuracy với
    kết quả trước khi lưu.
7.  **Kiểm tra tài liệu:** đối chiếu README và AI_USAGE với notebook để
    đảm bảo tên lớp, tham số, số epoch, đường dẫn và các chức năng được
    mô tả chính xác.

### Lưu ý về tính minh bạch

Notebook cho thấy các bước và mã nguồn được thực hiện, nhưng không tự
cho biết lịch sử sử dụng AI hoặc quyền tác giả của từng đoạn code. Nhóm
cần tự khai báo trung thực dựa trên quá trình làm việc thực tế. Không
nên khẳng định AI đã tạo một phần code cụ thể hoặc sinh viên đã tự
viết/chỉnh sửa phần đó nếu không xác minh được.
