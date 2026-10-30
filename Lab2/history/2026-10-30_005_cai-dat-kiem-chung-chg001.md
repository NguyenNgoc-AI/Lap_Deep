# LOG-006 — Cài và kiểm chứng CHG-001

- Ngày: 2026-10-30 (Asia/Saigon). WF-001 v1.0 LOCKED; CHG-001.
- Người dùng trả lời “ok” cho đề xuất CHG-001: GATE B APPROVED. GATE A đã duyệt trước.
- Kết quả: CHG-001 IMPLEMENTED / TESTED trong phạm vi cài đặt và kiểm tra sơ bộ. WF-001 chưa hoàn tất; phase/notebook/benchmark chưa triển khai hoặc nghiệm thu.

## Hiện trạng, checkpoint và thay đổi

- Đọc PROJECT_STATE và CHG-001 trước khi thực hiện. Test-Path xác nhận requirements.txt và .venv chưa tồn tại.
- WF LOCKED vẫn có SHA256 9DD04E4675CE28410D83400A050447157D6D90D29C7353E0A7AE85C121E31AC8.
- Tạo D:\Lab2\requirements.txt đúng AFTER đã duyệt; đối chiếu văn bản PASS. SHA256: 71E75C313BC808DBE5CA86B0B6C54C4C90D64786E5815BA33D6A4303DD00DCA2.
- BEFORE requirements.txt = Chưa tồn tại. AFTER đầy đủ:
```text
--index-url https://pypi.org/simple
--extra-index-url https://download.pytorch.org/whl/xpu
torch==2.14.1+xpu
torchvision==0.29.1+xpu
tensorboard==2.21.0
notebook==7.6.3
ipykernel==7.4.0
```
- BEFORE .venv = Chưa tồn tại. AFTER = venv Python 3.14.5 và bộ thư viện trong pip freeze bên dưới.
- Tạo .venv và pip install bằng đúng lệnh ở [CHG-001](../workflows/CHG-001_PROPOSED_environment.md). Không đổi pin hoặc thêm code dự án.
- Không có Git/commit; điểm trước thay đổi là hai đường dẫn chưa tồn tại. Không rollback, không xóa file.
- Cập nhật PROJECT_STATE, tạo log này. Bản WF LOCKED và các log cũ giữ nguyên.

## Lỗi môi trường và xử lý

- Lần tạo venv trong sandbox lỗi ensurepip exit 1. Chạy lại cùng lệnh với quyền ngoài sandbox hoàn tất exit 0; giữ nguyên venv mới của lượt này.
- Lần pip install trong sandbox không phân giải được PyPI/PyTorch, exit 1. Thông báo “No matching distribution” ở lần này đi kèm lỗi DNS, không phải bằng chứng thiếu wheel.
- Chạy lại đúng lệnh với quyền mạng ngoài sandbox: tải được toàn bộ wheel, cài thành công exit 0. Không dùng source build, không đổi thư viện đã duyệt.
- Tải mạng chậm; MKL 180.8 MB hoàn tất sau khoảng 10 phút 18 giây theo pip. Đã đọc trạng thái process/tệp tạm và HEAD metadata để chẩn đoán; không dừng hoặc chạy lại lượt cài đang tải.
- Pip sandbox cảnh báo không dọn được một số thư mục tạm của lượt lỗi; không tự xóa các thư mục này. Không cập nhật pip dù có thông báo bản mới.
- Không sửa driver/PATH hoặc Python hệ thống, không đăng ký kernel vào user scope. Chưa tải dataset/pretrained weights.

## Kiểm chứng thực tế

Lệnh kiểm tra đúng phần “Kiểm chứng sau cài” của CHG-001, chạy Python trong D:\Lab2\.venv.

- pip check: exit 0, “No broken requirements found.”
- Import torch, torchvision, tensorboard, notebook, ipykernel: thành công.
- Phép tính tensor CPU và XPU: kỳ vọng [2.0, 2.0], thực tế khớp, exit 0.
- Output:
```text
python D:\Lab2\.venv\Scripts\python.exe
torch 2.14.1+xpu torchvision 0.29.1+xpu
cpu [2.0, 2.0]
xpu_available True
xpu_device Intel(R) Arc(TM) Graphics
xpu_tensor [2.0, 2.0]
```
- pip freeze: exit 0; danh sách bên dưới là phiên bản đã cài thực, không phải dependency lock có hash.
- Giới hạn: chưa forward/backward DenseNet, chưa đo thời gian training, chưa mở Jupyter/TensorBoard UI hoặc kiểm chứng event scalar. TEST-001..005 đầy đủ của WF chưa hoàn tất. Không tuyên bố phase TESTED/ACCEPTED hoặc toàn WF thành công chỉ từ phép tính tensor.
- Kiểm chứng tài liệu cuối phiên: đọc lại log/state, kiểm tra hash requirements và WF không đổi.

## pip freeze

```text
absl-py==2.5.1
anyio==4.15.1
argon2-cffi==25.1.0
argon2-cffi-bindings==26.1.0
arrow==1.4.0
asttokens==3.0.2
async-lru==2.4.0
attrs==26.1.0
babel==2.18.0
beautifulsoup4==4.15.0
bleach==6.4.0
certifi==2026.10.23
cffi==2.1.1
charset-normalizer==3.5.2
colorama==0.4.6
comm==0.2.3
debugpy==1.8.22
defusedxml==0.7.1
dpcpp-cpp-rt==2026.1.0
executing==2.3.0
fastjsonschema==2.22.2
filelock==4.2.4
fqdn==1.6.0
fsspec==2026.9.0
grpcio==1.85.0
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.20
intel-cmplr-lib-rt==2026.1.0
intel-cmplr-lib-ur==2026.1.0
intel-cmplr-lic-rt==2026.1.0
intel-opencl-rt==2026.1.0
intel-openmp==2026.1.0
intel-pti==1.0.1
intel-sycl-rt==2026.1.0
ipykernel==7.4.0
ipython==9.17.1
ipython_pygments_lexers==1.1.1
isoduration==20.11.0
jedi==0.20.1
Jinja2==3.1.6
json5==0.17.3
jsonpointer==3.6
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
jupyter-events==0.12.1
jupyter-lsp==2.3.1
jupyter_builder==1.2.4
jupyter_client==8.10.0
jupyter_core==5.9.1
jupyter_server==2.21.1
jupyter_server_terminals==0.5.4
jupyterlab==4.6.5
jupyterlab_pygments==0.3.0
jupyterlab_server==2.28.1
lark==1.3.1
Markdown==3.11.2
MarkupSafe==3.0.4
matplotlib-inline==0.2.2
mistune==3.4.0
mkl==2026.1.0
mpmath==1.3.0
nbclient==0.11.0
nbconvert==7.17.2
nbformat==5.11.1
nest-asyncio2==1.7.4
networkx==3.7
notebook==7.6.3
notebook_shim==0.2.4
numpy==2.5.4
onemkl-license==2026.1.0
onemkl-sycl-blas==2026.1.0
onemkl-sycl-dft==2026.1.0
onemkl-sycl-lapack==2026.1.0
onemkl-sycl-rng==2026.1.0
onemkl-sycl-sparse==2026.1.0
packaging==26.3
pandocfilters==1.5.1
parso==0.8.7
pillow==13.0.0
platformdirs==4.14.0
prometheus_client==0.26.0
prompt_toolkit==3.0.53
protobuf==7.36.2
psutil==7.2.2
pure_eval==0.2.4
pycparser==3.12
pyelftools==0.33
Pygments==2.21.0
python-dateutil==3.0.0
python-json-logger==4.2.0
pywinpty==3.1.2
PyYAML==6.0.3
pyzmq==27.2.0
referencing==0.37.0
requests==2.34.2
rfc3339-validator==0.1.4
rfc3986-validator==0.1.1
rfc3987-syntax==1.1.0
rpds-py==2026.9.1
Send2Trash==2.1.0
setuptools==84.2.1
six==1.17.0
soupsieve==3.0.4
stack-data==0.6.3
sympy==1.14.0
tbb==2023.1.0
tcmlib==1.5.0
tensorboard==2.21.0
tensorboard-data-server==0.7.2
terminado==0.18.1
tinycss2==1.5.1
torch==2.14.1+xpu
torchvision==0.29.1+xpu
tornado==6.6
traitlets==5.16.1
triton-xpu==3.8.0
typing_extensions==4.16.0
tzdata==2026.6
umf==1.1.0
uri-template==1.3.0
urllib3==2.8.0
wcwidth==0.9.4
webcolors==25.10.0
webencodings==0.6.1
websocket-client==1.9.2
Werkzeug==3.1.9
```

## Tiếp theo

Chuẩn bị CHG với BEFORE/AFTER cho phase_01_environment.py, main.ipynb và test; sau duyệt mới chạy benchmark/TensorBoard theo WF-001. CHG-001 không cấp quyền tạo các file kỹ thuật đó.

