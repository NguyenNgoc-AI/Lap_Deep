# CHG-DATA-002 · đề xuất · chờ Gate B

Trong src/phases/phase_02_data.py, hàm run có thể nhận lại audit phiên bản cũ chỉ vì manifest khớp checksum cũ. Dữ liệu do CHG-DATA-001 tạo cần nhận diện riêng. Giữ khóa version hiện có vì nó mô tả nguồn Intel v2. Chỉ thêm trường nhận diện thuật toán. Nếu gặp cache cũ thì dừng và chỉ rõ đường dẫn cần lưu trữ trước khi tạo lại. Không xóa tự động.

Vị trí đọc audit, BEFORE:

```python
        audit = read_json(OUT / 'audit.json')
```

AFTER:

```python
        audit = read_json(OUT / 'audit.json')
        if audit.get('image_hash') != 'sha256-rgb-size-v1':
            raise ValueError(f'Legacy image hash: archive {OUT} before rebuilding the manifest')
```

Vị trí ghi audit, BEFORE:

```python
             'manifest_sha256': sha256(MANIFEST), 'classes': CLASSES,
```

AFTER:

```python
             'manifest_sha256': sha256(MANIFEST), 'classes': CLASSES,
             'image_hash': 'sha256-rgb-size-v1',
```

Kiểm tra trong thư mục tạm: audit cũ bị từ chối, audit mới với checksum khớp được đọc lại, manifest sai checksum vẫn bị từ chối. Sao lưu module trước khi áp dụng. Đây là phần bảo vệ manifest, chưa bao gồm toàn bộ P01.
