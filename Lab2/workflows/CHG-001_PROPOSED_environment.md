# CHG-001 — Tạo venv và cài bộ thư viện local

- WF-001 v1.0 LOCKED; ngày 2026-10-30 (Asia/Saigon).
- GATE A: APPROVED. GATE B: PENDING, đề xuất chưa thực hiện.
- Mục tiêu: tạo môi trường riêng để kiểm chứng import/CPU/XPU; chưa tạo phase/notebook hoặc chạy benchmark.

## Hiện trạng đã xác minh

- Windows 11 Home Single Language 64-bit, build 10.0.26200; registry DisplayVersion 25H2. Tên ProductName trong registry còn ghi Windows 10; dùng Caption Win32_OperatingSystem để xác nhận Windows 11.
- Python 3.14.5 64-bit tại C:\Users\toite\AppData\Local\Python\pythoncore-3.14-64\python.exe; pip 26.1.1; có module venv.
- Intel Arc Graphics, driver 32.0.101.9150, ngày driver trả về 2026-10-08. Chưa xác minh XPU runtime.
- D trống khoảng 164.2 GB; requirements.txt và .venv chưa tồn tại (Test-Path=False). Không có .git hoặc AGENTS.md trong workspace tại lúc khảo sát.
- PyTorch xác nhận cặp torch 2.14.1 / torchvision 0.29.1; index XPU có wheel cp314-cp314-win_amd64 cho cả hai.
- PyPI metadata: tensorboard 2.21.0 yêu cầu Python >=3.9; notebook 7.6.3 >=3.10; ipykernel 7.4.0 >=3.11. Chưa giải dependency hoặc kiểm thử cài; metadata không bảo đảm toàn bộ runtime thành công.

## File D:\Lab2\requirements.txt

BEFORE:
```text
Chưa tồn tại
```

AFTER — chính xác nội dung sẽ ghi khi được duyệt:
```text
--index-url https://pypi.org/simple
--extra-index-url https://download.pytorch.org/whl/xpu
torch==2.14.1+xpu
torchvision==0.29.1+xpu
tensorboard==2.21.0
notebook==7.6.3
ipykernel==7.4.0
```

## Môi trường D:\Lab2\.venv

BEFORE: chưa tồn tại.
AFTER: venv từ Python 3.14.5 hiện có, chứa bộ thư viện trên và phụ thuộc do pip giải. Thư viện trực tiếp được pin; dependency bắc cầu chưa khóa. Ghi pip freeze vào bằng chứng phiên sau khi cài thành công.

Lệnh PowerShell tuần tự; chỉ chạy lệnh kế tiếp khi lệnh trước thành công:
```powershell
& 'C:\Users\toite\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m venv 'D:\Lab2\.venv'
& 'D:\Lab2\.venv\Scripts\python.exe' -m pip install --no-cache-dir --only-binary=:all: -r 'D:\Lab2\requirements.txt'
```

## Kiểm chứng sau cài

```powershell
& 'D:\Lab2\.venv\Scripts\python.exe' -m pip check
& 'D:\Lab2\.venv\Scripts\python.exe' -c 'import sys,torch,torchvision,tensorboard,notebook,ipykernel; print("python",sys.executable); print("torch",torch.__version__,"torchvision",torchvision.__version__); print("cpu",(torch.ones(2)+1).tolist()); available=torch.xpu.is_available(); print("xpu_available",available); print("xpu_device",torch.xpu.get_device_name(0) if available else "UNAVAILABLE"); print("xpu_tensor",(torch.ones(2,device="xpu")+1).cpu().tolist() if available else "SKIPPED")'
& 'D:\Lab2\.venv\Scripts\python.exe' -m pip freeze
```

- PASS cài đặt: pip install và pip check thành công, import đủ, executable nằm trong .venv, CPU trả [2.0,2.0].
- XPU PASS sơ bộ: available=True, tên GPU đúng, phép tính XPU trả [2.0,2.0]. Đây chưa phải PASS benchmark/training.
- XPU False: ghi UNAVAILABLE/SKIPPED, giữ CPU dự phòng minh bạch; không tuyên bố GPU thành công. XPU ném lỗi: lưu lỗi, chưa đánh dấu kiểm tra GPU passed.
- Không có wheel/dependency xung đột: dừng cài, báo nguyên nhân, trình lại CHG nếu phải đổi pin; không build source hoặc đổi version tự động.

## Tác động / checkpoint / khôi phục

- Ghi requirements.txt và .venv trong D:\Lab2; pip dùng thư mục tạm của Windows khi giải nén. Có tải mạng từ PyPI và kho PyTorch, lượng tải và dung lượng cài thực chưa đo. Dự trù khoảng trống 15 GB để thao tác; không coi đây là kích thước gói đã xác minh.
- Không sửa Python hệ thống, PATH, driver, kernel người dùng hoặc dataset. Không cần quyền admin cho venv; quyền mạng/sandbox có thể được yêu cầu riêng.
- Điểm khôi phục: xác nhận hai đường dẫn chưa tồn tại trước khi chạy và giữ hash/file BEFORE của tài liệu liên quan trong LOG. Nếu đường dẫn bất ngờ tồn tại, dừng để đọc lại; không ghi đè.
- Nếu lỗi, giữ báo cáo và venv chưa hoàn tất để chẩn đoán; không tự xóa/rollback. Chỉ xóa các tài nguyên mới thuộc CHG nếu người dùng duyệt khôi phục riêng.
- Sau CHG-001 sẽ trình CHG cho phase/notebook/test và benchmark theo WF; chúng chưa được cấp quyền bởi đề xuất này.

## Nguồn đã đối chiếu

- https://pytorch.org/get-started/previous-versions/
- https://download.pytorch.org/whl/xpu/torch/
- https://download.pytorch.org/whl/xpu/torchvision/
- https://pypi.org/pypi/tensorboard/json
- https://pypi.org/pypi/notebook/json
- https://pypi.org/pypi/ipykernel/json
