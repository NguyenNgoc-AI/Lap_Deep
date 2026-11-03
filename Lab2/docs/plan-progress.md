# Nghiệm thu WF-LAB2-001 · 03/11/2026

[Description](labs2-description.md) → [workflow đã khóa](../workflows/WF-LAB2-001.md) → sinh code → smoke → chạy chính thức → đối chiếu dưới đây. Các số liệu là của bản chia theo nhóm cảnh.

| Phase | Code và phép kiểm | Bằng chứng / kết luận |
|---|---|---|
| P01 · Data | [Tạo manifest theo nhóm cảnh](../outputs/scene-review/build_manifest.py); [Scenes và loader](../src/phases/phase_02_data.py) tạo batch. Kiểm tra trùng nội dung, rà cặp gần trùng, đếm theo lớp và giữ test cố định. | PASS · [Bảng chia cuối](../outputs/scene-review/report.md): 11.173 train, 2.793 validation, 3.000 test. Majority baseline 500/2.793 = 17,90% trên validation. |
| P02 · Model | [build](../src/phases/phase_03_models.py) thay classifier sáu lớp; kiểm tra logits, tham số cập nhật, backbone và thống kê BatchNorm khi đóng băng. | PASS · Hai model × hai stage × hai cỡ batch. [Kiểm tra stage](../outputs/models/stage-checks.json), [kiến trúc và số tham số](model.md). |
| P03 · Training | [train_stages](../src/phases/phase_04_train.py) dùng Adam và cross-entropy; kiểm tra chuyển stage, dừng sớm, resume và reload best. | PASS · [Smoke](../outputs/smoke-entry-p03/checks.json), [bảng normal và đường học](../outputs/training-scene-v1/TRAINING.md), [quyết định bằng validation](../outputs/training-scene-v1/report.json). |
| P04 · Evaluation | [run](../evaluation/scene.py) tái hiện validation sau reload rồi đối chiếu dự đoán test, support và đường chéo confusion matrix. | PASS · 2.793/3.000 đúng; 207 sai; macro-F1 0,9326. [Bảng từng lớp, ma trận, ví dụ lỗi](../outputs/evaluation-scene-v1/report.md). |
| P05 · Demo | [predict](../evaluation/demo.py) nhận một ảnh và trả nhãn, điểm, run, stage, epoch. Đối chiếu với P04 rồi dùng ảnh không nhãn. | PASS · [Smoke: sai lệch điểm bằng 0](../outputs/smoke-p05/check.json); [normal: 10004.jpg → street](../outputs/demo-scene-v1/result.json); [hướng dẫn](demo.md). |

**So sánh run.** Tổng thời gian các epoch theo log: VGG11 43,7 phút (10 epoch), DenseNet121 48,8 phút (12 epoch), nhánh VGG LR thấp 23,2 phút (5 epoch bổ sung). DenseNet121 đúng nhiều hơn VGG11 hai ảnh validation, 2.613 so với 2.611 trên cùng 2.793 ảnh. Đây là căn cứ chọn checkpoint theo quy tắc đã định, chưa chứng minh DenseNet121 tốt hơn trên mọi lần chia.

**Dấu hiệu overfitting.** Từ epoch 7 đến 10 của VGG11, train loss giảm từ khoảng 0,12 xuống 0,07 nhưng validation loss tăng từ 0,20 lên 0,23. Với DenseNet121, từ epoch 9 đến 12 train loss giảm từ 0,128 xuống khoảng 0,09 trong khi validation loss tăng từ 0,188 lên khoảng 0,20. Vì thế dùng best.pt thay cho epoch cuối. [Log DenseNet121](../outputs/training-scene-v1/densenet121/history.json) · [Log VGG11](../outputs/training-scene-v1/vgg11/history.json).

**Phạm vi kết luận.** Một seed; tập test đã từng được xem trong phiên bản Lab trước. Kết quả không phải ước lượng trên nhiều lần chạy độc lập. EDA ban đầu vẫn được giữ để giải thích lý do phải sửa split; chỉ manifest sau rà nhóm cảnh được dùng để train.
**Baseline học được.** Khi chỉ huấn luyện classifier, cả hai model đạt best tại epoch 4 với 92,37% validation accuracy. Sau fine-tuning, VGG11 đạt 93,48% (+1,11 điểm phần trăm) và DenseNet121 đạt 93,56% (+1,18 điểm phần trăm). So sánh này dùng cùng tập validation và có ý nghĩa hơn việc chỉ so với baseline đoán lớp đa số.
