# Data — Rotten Tomatoes

## 1. Nguồn dữ liệu

| Mục | Nội dung |
|---|---|
| Tên trên Hugging Face Hub | `cornell-movie-review-data/rotten_tomatoes` |
| Nguồn gốc | Movie Review Data (Pang & Lee, 2005) |
| Nội dung | Câu review phim tiếng Anh ngắn, mỗi câu một nhãn cảm xúc |
| Nhãn | `0 = neg` (tiêu cực), `1 = pos` (tích cực) |
| Ngôn ngữ | Tiếng Anh, đã viết thường và tách dấu câu bằng khoảng trắng |

Lưu ý: bản `huggingface_hub` mới yêu cầu tên dạng `tổ_chức/tên`. Tên cũ `rotten_tomatoes` báo lỗi `HfUriError: Repository id must be 'namespace/name'`.

## 2. Cấu trúc và schema

Mỗi mẫu là một dòng với 2 trường:

| Trường | Kiểu | Ví dụ | Ghi chú |
|---|---|---|---|
| `text` | `string` | "the rock is destined to be …" | Câu review đã viết thường, dấu câu tách bằng khoảng trắng |
| `label` | `ClassLabel(names=['neg', 'pos'])` | `1` | 0 = neg, 1 = pos |

Sau tokenize, mỗi mẫu có thêm `input_ids` (list số nguyên, ≤ 128 phần tử) và `attention_mask` (1 = token thật, 0 = padding). File CSV xuất ra (`data/rotten_tomatoes/*.csv`) giữ 2 cột `text`, `label`.

## 3. Phân chia

| Tập | Số câu | Vai trò trong bài |
|---|---|---|
| train | 8.530 | Cập nhật trọng số khi fine-tune |
| validation | 1.066 | Theo dõi sau mỗi epoch; script dùng để chọn epoch tốt nhất |
| test | 1.066 | Chỉ dùng một lần ở bước đánh giá cuối |

Bộ dữ liệu đã chia sẵn 3 tập nên nhóm không tự tách. Không dùng tập test để chọn số epoch hay siêu tham số.

Ví dụ (train, nhãn `pos`):

> the rock is destined to be the 21st century's new " conan " and that he's going to make a splash even greater than arnold schwarzenegger , jean-claud van damme or steven segal .

## 4. Tiền xử lý

1. **Tokenize** bằng tokenizer của `distilbert-base-uncased` (WordPiece, chuyển về chữ thường): mỗi câu thành `input_ids` và `attention_mask`, thêm `[CLS]` (101) ở đầu và `[SEP]` (102) ở cuối.
2. **Cắt độ dài:** `truncation=True`, `max_length=128` token. Câu review rotten_tomatoes ngắn nên hầu hết không bị cắt.
3. **Padding động:** `DataCollatorWithPadding` chỉ pad đến câu dài nhất **trong từng batch**, thay vì pad mọi câu lên 128 → nhanh hơn và ít tốn bộ nhớ.
4. Áp dụng cho cả 3 tập bằng `dataset.map(tokenize_function, batched=True)`.
5. Tập train được xáo trộn với `seed=42`.

## 5. Hạn chế dữ liệu

- **Chỉ 2 nhãn:** câu trung tính hoặc vừa khen vừa chê vẫn bị gán vào một trong hai lớp.
- **Một miền:** chỉ là review phim; model có thể kém hơn với văn bản khác như review sản phẩm hay mạng xã hội.
- **Câu ngắn, viết thường, tách dấu câu:** khác cách viết của câu người dùng nhập ở demo (có chữ hoa, dấu câu liền chữ); tokenizer `uncased` giảm bớt nhưng không loại hết khác biệt.
- **Mỉa mai, phủ định phức tạp:** dữ liệu không đánh dấu riêng các trường hợp này nên không đo được model xử lý chúng tốt đến đâu.
- **Quy mô nhỏ:** 8.530 câu train; đủ cho bài thực hành nhưng dễ overfit nếu train nhiều epoch (xem [training.md](training.md)).
- Nhóm không tự kiểm tra trùng lặp hay nhãn sai trong dữ liệu; dùng nguyên bản chia sẵn của Hub.

## 6. Chạy và kết quả ghi ra

Trong thư mục `LAB 3`:

```powershell
D:\Code\.venv\Scripts\python.exe -m src.data
```

| Kết quả | Nội dung |
|---|---|
| `data/rotten_tomatoes/train.csv`, `validation.csv`, `test.csv` | Cột `text`, `label`; sau khi có các file này, các script đọc từ CSV, không cần mạng |
| `results/dataset_stats.json` | Số câu, phân bố nhãn, số từ trung bình và dài nhất của từng tập |

Lần chạy đầu cần mạng để tải dữ liệu từ Hugging Face Hub.
