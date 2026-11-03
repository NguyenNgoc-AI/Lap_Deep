# P04 · Đánh giá trên tập test

DenseNet121 epoch 9 đã được chọn bằng validation trước khi đánh giá test. Hàm run trong evaluation/scene.py đối chiếu checkpoint với manifest, ánh xạ lớp và phép biến đổi đã lưu, rồi nạp lại trên 2.793 ảnh validation. Kết quả khớp log P03: đúng 2.613 ảnh và loss 0,18784.

Trên 3.000 ảnh test, model đúng 2.793 ảnh, sai 207, accuracy 93,10%, macro-F1 93,26%, cross-entropy trung bình 0,18698. Số hàng dự đoán và đường dẫn khớp manifest, tổng các ô confusion matrix là 3.000 và tổng đường chéo là 2.793. Hai chiều glacier/mountain chiếm 112/207 lỗi (54,1%). Hai chiều buildings/street thêm 50 lỗi. Hai cặp lớp này chiếm 162/207 lỗi (78,3%). Forest có recall 473/474. Glacier có recall thấp nhất, 468/553.

[Metrics từng lớp, ma trận và ví dụ sai](../outputs/evaluation-scene-v1/report.md) · [Dự đoán từng ảnh](../outputs/evaluation-scene-v1/predictions.csv) · [Notebook đã chạy](../notebooks/main.ipynb).

Chạy lại bằng python -m evaluation.scene hoặc mở main.ipynb. Module tái sử dụng kết quả nếu checkpoint, manifest và checksum dự đoán khớp. Test từng được xem ở lần làm Lab trước. Kết quả thuộc một seed.
