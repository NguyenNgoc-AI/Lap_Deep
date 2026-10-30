# CHG-002 — PHASE-01, notebook và kiểm thử

- Ngày 2026-10-30; WF-001 v1.0 LOCKED, GATE A APPROVED; GATE B PENDING.
- Phạm vi: tạo ba file dưới đây, kernel lab2 trong .venv, chạy unittest và notebook benchmark, ghi report JSON/TensorBoard và notebook đã chạy trong outputs/environment. Chưa tải dataset hoặc pretrained weights.
- BEFORE của cả ba file: Chưa tồn tại, đã kiểm tra trực tiếp. Không thay requirements hoặc WF đã khóa.
- CPU/XPU tuần tự; 3 warm-up + 10 bước đo; batch 8, thử lại cả hai ở batch 4 khi OOM. SGD lr=0.01; seed=42. Backbone ở eval để BatchNorm buffers không đổi.
- Mỗi lần chạy có thư mục riêng, phiên bản thư viện/hash source/config; trạng thái và traceback được lưu. GPU lỗi thật làm phase FAILED; GPU không khả dụng được SKIPPED rõ ràng. OOM được phép phục hồi theo WF, lịch sử lỗi vẫn được giữ.
- Timing gồm forward/loss/backward/optimizer, có synchronize XPU; không gồm tạo input, hash tham số, ghi/read TensorBoard. Kết quả chỉ áp dụng classifier-only với weights ngẫu nhiên và fixture, không phải chất lượng pretrained.
- Tests điều khiển dùng mock được ghi rõ, không dùng mock làm bằng chứng GPU; kiểm chứng thực chạy notebook gọi DenseNet thật.
- Điểm khôi phục: ba file mới chưa tồn tại. Trước ghi kiểm tra lại; nếu có thay đổi dừng. Không tự rollback/xóa. Output mỗi lần chạy mới; file notebook nguồn giữ outputs rỗng, bản chạy nằm ở outputs.

## AFTER — D:\\Lab2\\src\\phases\\phase_01_environment.py

```python
"""WF-001: synthetic DenseNet121 CPU/XPU environment check."""
import gc
import hashlib
import json
import math
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from importlib.metadata import distributions
from pathlib import Path

import torch
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from torch import nn
from torch.utils.tensorboard import SummaryWriter
from torchvision.models import densenet121

ROOT = Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(tensors):
    result = hashlib.sha256()
    for name, value in tensors.items():
        result.update(name.encode())
        result.update(value.detach().cpu().contiguous().numpy().tobytes())
    return result.hexdigest()


def benchmark(device, batch, seed, log_dir):
    torch.manual_seed(seed)
    model = densenet121(weights=None).requires_grad_(False)
    model.classifier = nn.Linear(model.classifier.in_features, 6)
    model.eval()  # Keep frozen BatchNorm buffers unchanged.
    backbone_before = digest(model.features.state_dict())
    classifier_before = digest(model.classifier.state_dict())
    generator = torch.Generator().manual_seed(seed)
    images = torch.randn(batch, 3, 224, 224, generator=generator)
    labels = torch.arange(batch, dtype=torch.int64) % 6
    fixture_hash = digest({"images": images, "labels": labels})
    model = model.to(device)
    images, labels = images.to(device), labels.to(device)
    optimizer = torch.optim.SGD(model.classifier.parameters(), lr=0.01)
    seconds = []

    def synchronize():
        if device == "xpu":
            torch.xpu.synchronize()

    with SummaryWriter(str(log_dir)) as writer:
        for step in range(13):
            synchronize()
            started = time.perf_counter()
            optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = nn.functional.cross_entropy(logits, labels)
            loss.backward()
            optimizer.step()
            synchronize()
            elapsed = time.perf_counter() - started
            value = loss.detach().cpu().item()
            require(tuple(logits.shape) == (batch, 6), "Unexpected output shape")
            require(math.isfinite(value), "Non-finite loss")
            require(math.isfinite(elapsed) and elapsed > 0, "Invalid timing")
            writer.add_scalar("loss", value, step)
            if step >= 3:
                seconds.append(elapsed)
                writer.add_scalar("step_seconds", elapsed, step)
    require(digest(model.features.state_dict()) == backbone_before,
            "Frozen backbone changed")
    require(digest(model.classifier.state_dict()) != classifier_before,
            "Classifier did not update")
    events = EventAccumulator(str(log_dir)).Reload()
    require(len(events.Scalars("loss")) == 13, "Missing TensorBoard loss")
    require(len(events.Scalars("step_seconds")) == 10, "Missing timing events")
    return {
        "status": "PASSED", "batch": batch, "shape": [batch, 6],
        "device_name": torch.xpu.get_device_name(0) if device == "xpu" else "CPU",
        "fixture_sha256": fixture_hash, "seconds": seconds,
        "mean_step_seconds": sum(seconds) / len(seconds),
        "backbone_unchanged": True, "classifier_updated": True,
        "tensorboard_verified": True, "log_dir": str(log_dir),
    }


def run(output_root=ROOT / "outputs" / "environment",
        devices=("cpu", "xpu"), batch=8, seed=42):
    if devices not in (("cpu",), ("xpu",), ("cpu", "xpu")):
        raise ValueError("devices must be ('cpu',), ('xpu',), or ('cpu', 'xpu')")
    if type(batch) is not int or batch != 8 or type(seed) is not int or seed < 0:
        raise ValueError("WF-001 starts with batch=8 and a non-negative integer seed")
    source = Path(__file__)
    requirements = ROOT / "requirements.txt"
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in (source, requirements)}
    directory = Path(output_root) / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    directory.mkdir(parents=True, exist_ok=False)
    report = {
        "phase": "PHASE-01", "version": "1.0", "status": "RUNNING",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "directory": str(directory), "executable": sys.executable,
        "python": sys.version, "os": platform.platform(),
        "packages": {d.metadata["Name"]: d.version for d in distributions()},
        "source_hashes": hashes, "input_version": "synthetic-v1",
        "config": {"devices": list(devices), "initial_batch": batch,
                   "seed": seed, "warmup": 3, "measured_steps": 10,
                   "weights": None, "optimizer": "SGD", "learning_rate": 0.01,
                   "cpu_threads": torch.get_num_threads()},
        "attempts": [],
    }
    report_path = directory / "report.json"

    def save():
        report_path.write_text(json.dumps(report, indent=2, allow_nan=False),
                               encoding="utf-8")

    save()
    try:
        xpu_available = torch.xpu.is_available() if "xpu" in devices else False
        for current_batch in (batch, 4):
            results = {}
            for device in devices:
                if device == "xpu" and not xpu_available:
                    results[device] = {"status": "SKIPPED", "reason": "XPU unavailable"}
                    continue
                try:
                    results[device] = benchmark(
                        device, current_batch, seed,
                        directory / f"batch_{current_batch}" / device)
                except Exception as error:
                    results[device] = {
                        "status": "FAILED", "oom": isinstance(error, torch.OutOfMemoryError),
                        "error": str(error), "traceback": traceback.format_exc(),
                    }
                gc.collect()
            report["attempts"].append({"batch": current_batch, "devices": results})
            save()
            if not any(r.get("oom", False) for r in results.values()):
                break
        statuses = [r["status"] for r in results.values()]
        report["status"] = (
            "PASSED" if "PASSED" in statuses and "FAILED" not in statuses else "FAILED"
        )
        require(all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h
                    for p, h in hashes.items()), "Source/config changed during execution")
    except Exception:
        report["status"] = "FAILED"
        report["traceback"] = traceback.format_exc()
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        save()
    return report
```

## AFTER — D:\\Lab2\\tests\\test_environment.py

```python
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import torch
from src.phases import phase_01_environment as phase


class EnvironmentTests(unittest.TestCase):
    def execute(self, available, effects):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(phase.torch.xpu, "is_available", return_value=available):
                with patch.object(phase, "benchmark", side_effect=effects) as mocked:
                    result = phase.run(directory)
            saved = json.loads((Path(result["directory"]) / "report.json").read_text())
            self.assertEqual(saved["status"], result["status"])
            return result, mocked.call_args_list

    def test_unavailable_xpu_is_skipped(self):
        result, calls = self.execute(False, [{"status": "PASSED"}])
        self.assertEqual(result["status"], "PASSED")
        self.assertEqual(result["attempts"][0]["devices"]["xpu"]["status"], "SKIPPED")
        self.assertEqual(len(calls), 1)

    def test_oom_retries_both_devices_at_same_batch(self):
        result, calls = self.execute(True, [
            {"status": "PASSED"}, torch.OutOfMemoryError("fixture"),
            {"status": "PASSED"}, {"status": "PASSED"},
        ])
        self.assertEqual(result["status"], "PASSED")
        self.assertEqual([(c.args[0], c.args[1]) for c in calls],
                         [("cpu", 8), ("xpu", 8), ("cpu", 4), ("xpu", 4)])
        self.assertTrue(result["attempts"][0]["devices"]["xpu"]["oom"])

    def test_oom_at_batch_four_stops(self):
        result, calls = self.execute(True, [
            {"status": "PASSED"}, torch.OutOfMemoryError("fixture"),
            {"status": "PASSED"}, torch.OutOfMemoryError("fixture"),
        ])
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(len(calls), 4)

    def test_runtime_error_is_not_hidden_or_retried(self):
        result, calls = self.execute(True, [
            {"status": "PASSED"}, RuntimeError("fixture"),
        ])
        self.assertEqual(result["status"], "FAILED")
        self.assertEqual(len(calls), 2)
        self.assertIn("RuntimeError", result["attempts"][0]["devices"]["xpu"]["traceback"])

    def test_invalid_batch_creates_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                phase.run(directory, batch=0)
            self.assertEqual(list(Path(directory).iterdir()), [])
```

## AFTER — D:\\Lab2\\notebooks\\main.ipynb

Notebook nbformat 4.4; metadata kernel lab2 / Lab2 (.venv), language Python 3.14.5. Một markdown cell và ba code cells, execution_count=null, outputs=[]; không thêm logic ngoài nội dung dưới đây. JSON đầy đủ lưu ở cuối tài liệu để đối chiếu.

Markdown cell:
> Lab 2 — WF-001 / PHASE-01. Run cells in order. Synthetic fixture, random weights; no dataset accuracy. For this one-phase workflow, running PHASE-01 is the full pipeline. After source/config/dependency changes, restart the kernel and rerun all cells.

Code cell 1:
```python
from pathlib import Path
import importlib
import inspect
import sys
from IPython.display import display

ROOT = Path.cwd().resolve()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
assert Path(sys.executable).resolve() == ROOT / ".venv" / "Scripts" / "python.exe", "Select Lab2 (.venv)"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.phases import phase_01_environment as phase

importlib.invalidate_caches()
phase = importlib.reload(phase)
print("PHASE-01: NOT_RUN")
print(inspect.getsource(phase))
```

Code cell 2:
```python
importlib.invalidate_caches()
phase = importlib.reload(phase)
print("PHASE-01: RUNNING")
report = phase.run()
print("PHASE-01:", report["status"])
display(report)
if report["status"] != "PASSED":
    raise RuntimeError(f"See errors in {report['directory']}/report.json")
```

Code cell 3:
```python
print("TensorBoard command:")
print(f'"{ROOT / ".venv" / "Scripts" / "tensorboard.exe"}" --logdir "{report["directory"]}" --host 127.0.0.1')
print("Synthetic environment check only; no dataset accuracy measured.")
```

## Thực thi sau duyệt

Tại D:\\Lab2, tuần tự; chỉ tiếp tục nếu lệnh trước thành công:

```powershell
& 'D:\Lab2\.venv\Scripts\python.exe' -m unittest discover -s tests -v
& 'D:\Lab2\.venv\Scripts\python.exe' -m ipykernel install --prefix 'D:\Lab2\.venv' --name lab2 --display-name 'Lab2 (.venv)'
& 'D:\Lab2\.venv\Scripts\python.exe' -m nbconvert --to notebook --execute 'D:\Lab2\notebooks\main.ipynb' --ExecutePreprocessor.kernel_name=lab2 --ExecutePreprocessor.timeout=1800 --output main.executed.ipynb --output-dir 'D:\Lab2\outputs\environment'
```

- Tạo thư mục outputs/environment trước nbconvert; tên notebook đã chạy nếu tồn tại sẽ dùng hậu tố timestamp, không ghi đè bằng chứng cũ.
- PASS: 5 unittest đạt; notebook đúng kernel chạy xong; real report có shape [B,6], loss hữu hạn, classifier thay đổi/backbone không đổi, 10 thời gian dương, TensorBoard 13 loss và 10 timing mỗi thiết bị thành công. Kiểm tra source thực khớp bản duyệt.
- Output: mỗi run có report.json + event files; notebook đã chạy ghi source thực/trạng thái/traceback. TEST-001..005 được đánh giá theo evidence, không tự ACCEPTED.
- Tác động: tải CPU/GPU cục bộ trong benchmark; có ghi thư viện cache/Jupyter runtime khi thực thi, không đổi driver/Python hệ thống; kernel đặt trong .venv/share/jupyter/kernels/lab2. Không thêm package.
- Không dùng cờ cho phép notebook bỏ qua lỗi. Nếu test/benchmark lỗi không thuộc nhánh OOM đã duyệt, lưu traceback và báo để sửa qua CHG mới.

## JSON notebook đầy đủ

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# Lab 2 — WF-001 / PHASE-01\n",
        "Run cells in order. Synthetic fixture, random weights; no dataset accuracy.\n",
        "For this one-phase workflow, running PHASE-01 is the full pipeline.\n",
        "After source/config/dependency changes, restart the kernel and rerun all cells."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "from pathlib import Path\n",
        "import importlib\n",
        "import inspect\n",
        "import sys\n",
        "from IPython.display import display\n",
        "\n",
        "ROOT = Path.cwd().resolve()\n",
        "if ROOT.name == \"notebooks\":\n",
        "    ROOT = ROOT.parent\n",
        "assert Path(sys.executable).resolve() == ROOT / \".venv\" / \"Scripts\" / \"python.exe\", \"Select Lab2 (.venv)\"\n",
        "if str(ROOT) not in sys.path:\n",
        "    sys.path.insert(0, str(ROOT))\n",
        "from src.phases import phase_01_environment as phase\n",
        "\n",
        "importlib.invalidate_caches()\n",
        "phase = importlib.reload(phase)\n",
        "print(\"PHASE-01: NOT_RUN\")\n",
        "print(inspect.getsource(phase))\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "importlib.invalidate_caches()\n",
        "phase = importlib.reload(phase)\n",
        "print(\"PHASE-01: RUNNING\")\n",
        "report = phase.run()\n",
        "print(\"PHASE-01:\", report[\"status\"])\n",
        "display(report)\n",
        "if report[\"status\"] != \"PASSED\":\n",
        "    raise RuntimeError(f\"See errors in {report['directory']}/report.json\")\n"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": null,
      "metadata": {},
      "outputs": [],
      "source": [
        "print(\"TensorBoard command:\")\n",
        "print(f'\"{ROOT / \".venv\" / \"Scripts\" / \"tensorboard.exe\"}\" --logdir \"{report[\"directory\"]}\" --host 127.0.0.1')\n",
        "print(\"Synthetic environment check only; no dataset accuracy measured.\")\n"
      ]
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Lab2 (.venv)",
      "language": "python",
      "name": "lab2"
    },
    "language_info": {
      "name": "python",
      "version": "3.14.5"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 4
}
```

