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
