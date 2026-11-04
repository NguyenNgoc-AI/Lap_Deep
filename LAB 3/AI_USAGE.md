# Tài liệu khai báo việc sử dụng AI — Lab 3

Phạm vi: Practice 3 — Get started with Hugging Face (Exercise 1, Exercise 2), nhánh `Lab3` của repo `NguyenNgoc-AI/Lap_Deep`.

Mục 1–7 khai báo phần của thành viên **HuHoww (HUYNH HUU HAO)**, dựa trên lịch sử trò chuyện thật với Claude từ 27/10 đến 01/11/2026. Mục 8 để các thành viên khác tự khai báo phần của mình.

## 1. Công cụ AI đã sử dụng

| Công cụ | Dùng cho |
|---|---|
| **Claude** (Anthropic), qua ứng dụng Claude | Giải thích đề, viết code, hướng dẫn cài đặt và sửa lỗi, phân tích kết quả, viết tài liệu |
| VS Code, Jupyter, PowerShell | Môi trường chạy notebook và script — công cụ phát triển, không phải AI |
| GitHub (web) | Lưu và chia sẻ bài — không phải AI |

Không dùng công cụ AI nào khác cho phần việc khai báo ở đây.

## 2. Mục đích sử dụng AI

| Ngày | Việc nhờ Claude |
|---|---|
| 27/10 | Giải thích đề Practice 3: hai bài yêu cầu gì, cần nộp gì, các link tham khảo có phải tải không, nên bắt đầu từ đâu, làm trên VS Code được không |
| 28/10 | Hướng dẫn cài thư viện vào `.venv`, chọn kernel; viết code Exercise 1 và Exercise 2 |
| 28/10 | Hướng dẫn cài PyTorch bản CUDA cho GPU RTX 3050 và xử lý chuỗi lỗi khi cài |
| 28/10 | Sửa lỗi `HfUriError` khi tải dữ liệu; đọc kết quả, phân tích overfitting, viết ô nhận xét |
| 28/10 | Kiểm tra hai notebook so với đề; hướng dẫn đưa bài lên GitHub |
| 01/11 | Xem cấu trúc repo nhóm (Lab 1, Lab 2), tách Exercise 2 thành các file `src/`, viết README, `docs/`, `AI_USAGE.md` và báo cáo |
| 04/11 | Rà soát Lab 3 theo `RULES.md` v1.1 (nhánh `lab2.1`): đổi tên file `docs/`, bổ sung nội dung còn thiếu, tạo `PROJECT_STATE.md` và `history/` |
| 04/11 | Hướng dẫn push bằng Git/VS Code; xử lý lỗi môi trường sau khi cài lại Windows (thiếu Git, mất Python gốc của `.venv`, thiếu `ipykernel`); đọc kết quả chạy lại ex2 và điền vào tài liệu |

AI không được dùng làm nguồn xác nhận kết quả. Mọi con số trong tài liệu lấy từ output thật của notebook.

## 3. Đóng góp của sinh viên (HuHoww)

- Chọn làm bài trên VS Code với môi trường `.venv` trên máy cá nhân, và tách mỗi bài thành một notebook riêng.
- Tự cài đặt, chạy toàn bộ các lệnh và notebook trên máy mình; chụp màn hình output và lỗi gửi lại để xử lý.
- Tự sửa tên dữ liệu/model trong notebook Exercise 2 theo hướng dẫn và chạy lại đến khi thành công (3 epoch trên GPU, 28/10).
- Đưa ra yêu cầu về cấu trúc thư mục theo bảng của giảng viên (`docs/` gồm description, data, model, training, evaluation, demo, progress status) và yêu cầu đối chiếu với Lab 1, Lab 2.
- Đưa bài lên GitHub, xóa thư mục `LAB 3` khỏi nhánh `main` vì đã có ở nhánh `Lab3`.

## 4. Các thành phần có sự hỗ trợ đáng kể từ AI

| Thành phần | Mức độ | Ghi chú |
|---|---|---|
| Code Exercise 1 (`notebooks/ex1_sentiment_analysis.ipynb`) | Claude viết | Sinh viên chạy trên máy mình và lưu output |
| Code Exercise 2 bản đầu (7 bước) | Claude viết | Ban đầu cho CPU (2.000 câu), sau chỉnh cho GPU (toàn bộ dữ liệu, `fp16`, 3 epoch) |
| Hai file notebook hiện tại | Claude tạo lại file | File `lab3.ipynb` ban đầu bị mất trên máy; Claude tạo lại hai notebook qua kết nối với máy tính |
| Ô "Nhận xét" của Exercise 1 và bản đầu Exercise 2 | Claude viết | Dựa trên output thật do sinh viên chạy |
| Sửa ex2 ngày 30/10 (tách validation/test) | **Không thuộc phần này** | Do HoangKhanh1904 thực hiện — xem mục 8 |
| `src/` (`config`, `data`, `model`, `train`, `evaluation`, `demo`) | Claude viết | Chưa chạy với model và dữ liệu thật |
| `README.md`, `docs/*.md`, `requirements.txt`, `.gitignore`, `AI_USAGE.md`, `PROJECT_STATE.md`, báo cáo | Claude viết | Số liệu lấy từ output notebook |
| `history/*.md` | Claude viết | Log trước 04/11 là log ghi bù từ lịch sử trò chuyện và commit; log 30/10 chỉ dựa trên diff, người sửa cần bổ sung |
| Hướng dẫn cài PyTorch CUDA và sửa lỗi môi trường | Claude hướng dẫn | Sinh viên tự thực hiện các lệnh |

## 5. Mục đích của các nhóm câu lệnh (prompt)

Ghi theo mục đích, không phải nguyên văn.

| Nhóm prompt | Ví dụ thực tế (diễn đạt lại) | Mục đích |
|---|---|---|
| Hiểu đề | "Đề tài này tôi phải làm những gì?", "Có cần bấm vào link để tải không?" | Nắm yêu cầu hai bài và phần cần nộp |
| Cách bắt đầu | "Bắt đầu làm gì đầu tiên?", "Làm bằng VS Code không được hả?" | Chọn môi trường và thứ tự làm |
| Viết code | "Dán bước 4 và 5 vào đâu?" | Nhận code từng bước và vị trí đặt code |
| Sửa lỗi môi trường | Gửi ảnh lỗi `Torch not compiled with CUDA enabled`, `Access is denied … c10.dll`, `module 'torch' has no attribute '__version__'`, lỗi build numpy | Cài được PyTorch bản GPU |
| Sửa lỗi code | Gửi ảnh lỗi `HfUriError` | Tải được dữ liệu và model |
| Kiểm tra kết quả | "Kết quả như này là ổn chưa?", "2 file có đúng đề không?" | Đối chiếu output với đề |
| Tổ chức và nộp bài | "Up lên GitHub thế nào?", "Lab 3 thiếu file gì? Xem kỹ Lab 1, Lab 2", "Làm file report", "Đọc lại toàn bộ yêu cầu xem cần bổ sung gì" | Hoàn thiện cấu trúc và tài liệu theo yêu cầu giảng viên |

## 6. Những chỉnh sửa của sinh viên

- Chạy code AI viết trên máy thật, phát hiện lỗi thực tế (tên dữ liệu kiểu cũ, PyTorch bản CPU) và yêu cầu sửa; code chỉ được giữ lại sau khi chạy thành công.
- Sửa tên `rotten_tomatoes` → `cornell-movie-review-data/rotten_tomatoes` và `distilbert-base-uncased` → `distilbert/distilbert-base-uncased` trong notebook.
- Không giữ phương án AI đề xuất ban đầu (tạo repo mới bằng "Publish to GitHub") vì nhóm đã có repo chung; chuyển sang đưa bài vào repo `Lap_Deep`.
- Yêu cầu AI đọc lại bản ex2 mới nhất trên nhánh `Lab3` thay vì bản cũ, và sửa cấu trúc tài liệu theo đúng danh sách của giảng viên.

## 7. Phương pháp kiểm chứng

| Bước | Đã làm | Kết quả |
|---|---|---|
| Kiểm tra môi trường | Có | `torch 2.14.1+cu126`, `cuda.is_available() = True`, RTX 3050 6GB |
| Kiểm tra dữ liệu | Có | 8.530 / 1.066 / 1.066 câu, 2 nhãn `neg`/`pos` |
| Kiểm tra huấn luyện | Có (lần 1) | Đủ 3 epoch, 1.602 bước, loss train giảm 0.4002 → 0.1447 |
| Đối chiếu số liệu | Có | Mọi con số trong README, `docs/`, báo cáo đối chiếu với output notebook |
| Đối chiếu notebook với đề | Có | Đủ 4 yêu cầu Ex1 và 7 yêu cầu Ex2 |
| Chạy script `src/` | Một phần | Chạy đủ chuỗi data → demo không lỗi với model tí hon, dữ liệu giả lập; **chưa chạy với model và dữ liệu thật** |
| Chạy lại ex2 bản 30/10 đủ 3 epoch | Có (04/11) | GPU, 121,8 giây; test 84.62%, F1 84.67%; trùng kết quả lần 28/10 |

### Lưu ý về tính minh bạch

Phần lớn code và tài liệu Lab 3 do Claude viết theo yêu cầu và dưới sự kiểm tra của sinh viên; sinh viên chịu trách nhiệm chạy, kiểm tra kết quả và quyết định nội dung nộp. Khi chạy lại ex2 và các script, phải cập nhật số liệu thật vào tài liệu, không dùng số do AI ước lượng.

## 8. Khai báo của các thành viên khác

Mỗi thành viên tự điền phần của mình (công cụ AI đã dùng, việc nhờ AI, phần tự làm). Phần dưới chưa được điền.

| Thành viên | Phần việc trong Lab 3 | Công cụ AI | Nội dung nhờ AI hỗ trợ |
|---|---|---|---|
| HoangKhanh1904 | Sửa ex2 ngày 30/10: tách validation/test, đánh giá test riêng, viết lại nhận xét | Chưa khai báo | Chưa khai báo |
| (thành viên khác) | | | |
