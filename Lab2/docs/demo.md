# P05 · Từ một ảnh tới dự đoán

Đầu vào là một ảnh đọc được bằng Pillow. [Hàm predict](../evaluation/demo.py) đọc ảnh thành RGB, áp dụng cùng phép resize, center crop và chuẩn hóa như P04. Hàm kiểm tra SHA-256 của best.pt, tên model, epoch và cấu hình transform trước khi suy luận ở chế độ eval. Chỉ số có logit cao nhất xác định nhãn theo danh sách lớp của checkpoint; softmax cho điểm của lớp đó. Điểm này chưa được hiệu chuẩn thành xác suất dự đoán đúng.

**Smoke run.** Dùng ảnh buildings/20057.jpg đã có dự đoán P04 để kiểm tra đường suy luận một ảnh. Kết quả là index 0, buildings, softmax 0,9992893934; chênh lệch so với P04 bằng 0 (ngưỡng 0,0001). [Log đối chiếu](../outputs/smoke-p05/check.json).

**Normal run.** [Ảnh 10004.jpg](../data/raw/intel-v2/seg_pred/seg_pred/10004.jpg) cho index 5, street, điểm 0,8663. Run densenet121, stage finetune, best epoch 9. [Kết quả với mã băm ảnh và checkpoint](../outputs/demo-scene-v1/result.json). Ảnh thuộc seg_pred nên ví dụ này minh họa cách model dự đoán, không đo accuracy.

Trong [notebook](../notebooks/main.ipynb), đổi IMAGE_PATH ở ô P05 để nhìn ảnh và kết quả. Từ PowerShell tại D:\Lab2:

```powershell
.\.venv\Scripts\python.exe -m evaluation.demo
.\.venv\Scripts\python.exe -m evaluation.demo "D:\duong-dan\anh.jpg"
```
