# 2026-11-13 · 001 · Tổng quan dự án và trực quan hóa dữ liệu

- Người yêu cầu: HuHoww. Công cụ: Claude.
- Yêu cầu: Lab 3 thiếu mô tả tổng quan dự án và trang data visualization (HTML).

## Đã làm

- `README.md`: thêm mục "Tổng quan dự án" (mục tiêu, bài toán, Ex1, Ex2, dữ liệu, phương pháp, môi trường, bảng kết quả chính, hạn chế, link trang trực quan hóa); thêm `visualize.py` vào cấu trúc thư mục và lệnh chạy.
- `src/visualize.py`: đọc `data/rotten_tomatoes/*.csv`, `results/train_log.json`, `results/test_metrics.json`, `results/misclassified.csv`; tạo `results/data_visualization.html` (một file, không cần mạng, chỉ dùng thư viện chuẩn Python). Thiếu file kết quả nào thì bỏ phần đó.
- Bổ sung phần EDA vào trang (theo yêu cầu thêm sơ đồ EDA): sơ đồ quy trình EDA 7 bước, kiểm tra chất lượng và rò rỉ dữ liệu, từ vựng, dấu hiệu ngôn ngữ theo nhãn, kết luận EDA.
- `docs/data.md` mục 7; cập nhật `plan-progress.md`, `PROJECT_STATE.md`, `AI_USAGE.md`.

## Kiểm chứng

- Chạy `python -m src.visualize` trên CSV và `results/` của nhánh `Lab3`; mở trang ở chế độ sáng, tối và màn hình điện thoại.
- Số liệu trên trang khớp `dataset_stats.json`, `train_log.json`, `test_metrics.json` (10.662 câu; validation 45.22% → 83.58% / 84.62% / 84.52%; confusion matrix [[459, 74], [90, 443]]; 82/164 câu sai có độ tin cậy > 90%); số liệu EDA tính lại trực tiếp từ CSV (0 câu rỗng/trùng/rò rỉ; OOV 6,44% validation, 6,26% test; phủ định 26,3% NEG, 17,2% POS).
- Không đổi code huấn luyện, không chạy lại model.
