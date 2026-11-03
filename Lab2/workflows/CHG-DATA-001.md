# CHG-DATA-001 · Gate B · đề xuất

File: src/phases/phase_02_data.py. Thêm trước inspect_images. BEFORE: chưa có hàm rgb_digest.

```python
def rgb_digest(image):
    from hashlib import sha256 as digest
    rgb = image.convert('RGB')
    width, height = rgb.size
    return digest(f'{width}x{height}:'.encode() + rgb.tobytes()).hexdigest()
```

Trong inspect_images, BEFORE:

```python
                                 class_name=name, label=label, sha256=sha256(path),
```

AFTER:

```python
                                 class_name=name, label=label, sha256=rgb_digest(image),
```

Hash file ZIP/manifest vẫn là hash byte file. Chỉ khóa nhóm ảnh đổi sang pixel RGB có kèm kích thước. Không phát hiện ảnh gần giống. Smoke dự kiến: cùng pixel khác metadata có cùng khóa, khác kích thước có khóa khác, nhóm trùng test không đi vào train/validation. Không dùng lại manifest/audit cũ. Backup trước sửa; hiện chưa ghi source.
