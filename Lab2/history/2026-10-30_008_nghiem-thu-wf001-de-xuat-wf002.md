# LOG-009 — Nghiệm thu WF-001, đề xuất WF-002

- Ngày 2026-10-30, Asia/Saigon. Người dùng: “ok làm đi”, trả lời yêu cầu nghiệm thu WF-001 và tiếp tục soạn workflow dữ liệu/thực nghiệm.
- APPROVED: WF-001 nghiệm thu, PHASE-01 ACCEPTED; WF-001 COMPLETED trong PROJECT_STATE. Không sửa nội dung WF-001 LOCKED hoặc log lịch sử.
- PENDING: WF-002 v1.0 mới soạn, GATE A chưa duyệt; chưa có GATE B/CHG cho dữ liệu và training thật.
- Trạng thái: NO_CODE_CHANGE; đọc hiện trạng/tài liệu/metadata, tạo đề xuất và ghi nhận nghiệm thu.

## Khảo sát và bằng chứng

- Đọc PROJECT_STATE, liệt kê workspace/workflows/history; đọc notebook hiện hữu và phần đầu source PHASE-01 để biết vị trí tích hợp. Không có data local; D trống khoảng160GB.
- Trang Kaggle qua web không trích xuất được nội dung; endpoint API qua web cũng không truy cập được. Đọc metadata công khai bằng Invoke-RestMethod ngoài sandbox, không dùng credentials hoặc tải ảnh.
- API datasets/list: ref=puneet6060/intel-image-classification, title Intel Image Classification, totalBytes363152213, lastUpdated2019-01-30; versionNumber null.
- API datasets/view: currentVersionNumber2, totalBytes368859597; mô tả khoảng25k ảnh150x150, 6 lớp buildings/forest/glacier/mountain/sea/street; khoảng14k train,3k test,7k prediction. LicenseName: Data files © Original Authors. Hai trường totalBytes khác nhau, chưa đo archive thực.
- Đọc tài liệu chính thức VGG11/DenseNet121. Metadata pretrained trước thayhead: VGG11 ~506.8MB, DenseNet121 ~30.8MB.
- Đọc enum/transform trong torchvision local: VGG11_Weights.IMAGENET1K_V1 và DenseNet121_Weights.IMAGENET1K_V1, resize256/crop224, ImageNet mean/std. Chỉ đọc metadata, không instantiate/train model hoặc tải weights.

## Đề xuất và tự phản biện

- Tạo workflows/WF-002_v1.0_DRAFT_intel-experiments.md với mục tiêu/phạm vi, input-output contracts, phases02–05, ma trận7run, checks, DoD và rollback.
- Sáu run transfer: VGG11/DenseNet121 × baseline(lr0.001,B8), đổiLR0.0003, đổiB16; 5epochs/run. Một run fine-tune model thắng validation thêm3epochs lr0.00001, mở block cuối/classifier.
- Chọn best theo validation trước khi dùng test; test chỉ đánh giá cuối, không chọn hyperparameter hoặc model theo test accuracy.
- VGG11 đóng băng cả các FC pretrained và chỉ train lớp cuối mới; DenseNet tương tự. Frozen BatchNorm/dropout eval; fine-tune giữ BN running stats, vẫn train affine phần được mở.
- Kiểm kê ảnh/nhãn/cấu trúc thực, loại trùng trong train bằng manifest, giữ raw/test; kiểm tra train-test exact duplicates. Chia train/val stratified seed42 sau lọc. Ảnh hỏng/nhãn xung đột dừng và báo, không bỏ ngầm.
- So sánh batch có khác số optimizer steps, fine-tune có ngân sách bổ sung; một seed không đủ kết luận thống kê. Không hứa accuracy/ETA hoặc lấy benchmark fixture làm thời gian train thật.
- GateB vẫn phải trình code/file/lệnh cụ thể; môi trường đã nghiệm thu không cấp quyền code mới chưa thấy. Quyền “làm đi” ở ngữ cảnh này là tiếp tục soạn workflow đã nêu trong phản hồi trước.

## File / kiểm chứng / trạng thái

- Tạo WF-002 DRAFT và log này; cập nhật PROJECT_STATE ghi nghiệm thu WF001, metadata dataset và đề xuấtWF002.
- Không thay code/notebook/requirements/driver, không tải dataset/weights hoặc train. BEFORE/AFTER code: không áp dụng. Test runtime mới: NOT_RUN; giữ bằng chứng đã PASS ở LOG-008.
- Đọc lại tài liệu, kiểm tra ma trận có7run, tách train/val/test và các cổng duyệt nhất quán. Không gọi proposal là APPROVED.
- Chưa có Git/commit hoặc rollback; giữ nguyên các file kỹ thuật và WF khóa. Bước tiếp theo: người dùng duyệt WF-002, sau đó trình CHG triển khai PHASE-02.

## Nguồn

- https://www.kaggle.com/datasets/puneet6060/intel-image-classification/data
- https://www.kaggle.com/api/v1/datasets/view/puneet6060/intel-image-classification
- https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.vgg11.html
- https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.densenet121.html
