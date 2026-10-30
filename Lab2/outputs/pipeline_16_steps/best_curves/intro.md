### Đường học của các run tốt nhất

“Tốt nhất” ở đây được xác định bằng **validation accuracy cao nhất**, sau đó xét validation loss, epoch và run ID khi hòa điểm. R07 là mô hình cuối; R02 và R06 lần lượt là run transfer tốt nhất của VGG11 và DenseNet121. Mỗi đường biểu diễn toàn bộ lịch sử của một run, không ghép điểm tốt nhất từ nhiều run thành một đường giả.

Hai biểu đồ đầu đặt train và validation của R07 cạnh nhau trên cùng hệ trục để quan sát khoảng cách khái quát hóa. Hai biểu đồ tiếp theo so sánh các run transfer tốt nhất trên cùng ngân sách 5 epoch. R07 bắt đầu từ checkpoint R02 và có thêm 3 epoch fine-tune, nên epoch của R07 là số đếm trong giai đoạn fine-tune.

R07 được chọn theo accuracy; điều này không có nghĩa nó có validation loss thấp nhất. Trong R07, epoch 1 có validation loss thấp nhất, còn epoch 3 có validation accuracy cao nhất. Hai điểm được đánh dấu riêng để làm rõ sự khác biệt giữa hai tiêu chí.