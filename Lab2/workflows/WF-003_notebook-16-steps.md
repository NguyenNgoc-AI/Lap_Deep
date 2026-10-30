# WF-003 / CHG-008 — Notebook 16 bước

Yêu cầu trực tiếp: viết một notebook theo chuỗi DEFINE PROBLEM → EDA → DATA SPLIT → CLEANING → FEATURE ENGINEERING → BASELINE MODEL → MODEL SELECTION → HYPERPARAMETER TUNING → TRAIN MODEL → EVALUATION METRICS → CROSS VALIDATION → EXPERIMENT MANAGEMENT → STATISTICAL VALIDATION → ERROR ANALYSIS → MODEL INTERPRETABILITY → BEST MODEL.

Triển khai theo quyền viết notebook của người dùng và chỉ thị tiếp tục đến hoàn tất trong phiên. BEFORE: notebook mới chưa tồn tại. File giao: notebooks/intel_pipeline_16_steps.ipynb, có nội dung tiếng Việt và output thực. Giữ nguyên source, config, raw, checkpoint và kết quả WF-002. Notebook dùng lại artifact đã xác minh cho bảy run, bổ sung EDA, majority baseline, CV linear probe, thống kê theo cặp, phân tích lỗi và Grad-CAM.

CV bổ sung: DenseNet121 ImageNet đóng băng hoàn toàn, đặc trưng center-crop 1024 chiều; train linear head mới cho từng fold, 5 fold phân tầng trên train+validation đã làm sạch, seed42, Adam lr0.001, batch256, 5epoch, không dùng test. Đây là protocol linear probe riêng, không phải CV của R07, không dùng chọn lại model. Có cache gắn fingerprint và log riêng trong outputs/pipeline_16_steps. Thống kê test mang tính phân tích hậu nghiệm, không dùng quyết định tuning.

Kiểm chứng: notebook chạy từ đầu đến cuối; đủ16section; không error; baseline/metrics/CI/McNemar/fold assertions; OOF đủ mỗi ảnh đúng1lần, không leakage hash; Grad-CAM hữu hạn, đúng kích thước; đối chiếu artifact WF002 không đổi. Cập nhật State và LOG-011, lưu notebook trước/sau thực thi và checksum. Không cài dependency mới.
