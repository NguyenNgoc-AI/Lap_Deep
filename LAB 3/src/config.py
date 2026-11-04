"""Cấu hình chung cho Lab 3 — Practice 3: Get started with Hugging Face.

Mọi đường dẫn tính từ thư mục gốc của Lab 3, nên các lệnh phải chạy
từ thư mục `LAB 3`, ví dụ:  python -m src.train
"""
import os
import sys
from pathlib import Path

# In tiếng Việt ổn định trên PowerShell/cmd của Windows
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# ---------------------------------------------------------------- Thư mục
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

# --------------------------------------------------------------- Exercise 1
# Model đã fine-tune sẵn cho phân tích cảm xúc (SST-2), dùng trực tiếp
SENTIMENT_MODEL = os.environ.get(
    "LAB3_SENTIMENT_MODEL",
    "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
)

# --------------------------------------------------------------- Exercise 2
DATASET_NAME = os.environ.get("LAB3_DATASET", "cornell-movie-review-data/rotten_tomatoes")
DATASET_CSV_DIR = DATA_DIR / "rotten_tomatoes"          # bản CSV xuất ra bởi src.data
BASE_MODEL = os.environ.get("LAB3_BASE_MODEL", "distilbert/distilbert-base-uncased")
FINETUNED_DIR = MODELS_DIR / "distilbert-rotten-tomatoes"  # model sau fine-tune
CHECKPOINT_DIR = MODELS_DIR / "checkpoints"                # checkpoint theo epoch

ID2LABEL = {0: "NEGATIVE", 1: "POSITIVE"}
LABEL2ID = {v: k for k, v in ID2LABEL.items()}

# Siêu tham số huấn luyện
SEED = 42
MAX_LENGTH = 128
LEARNING_RATE = 2e-5
TRAIN_BATCH_SIZE = 16
EVAL_BATCH_SIZE = 32
NUM_EPOCHS = 3
WEIGHT_DECAY = 0.01
LOGGING_STEPS = 50
# Giới hạn số câu train (None = toàn bộ). Máy chỉ có CPU nên đặt khoảng 2000.
TRAIN_LIMIT = int(os.environ["LAB3_TRAIN_LIMIT"]) if os.environ.get("LAB3_TRAIN_LIMIT") else None


def ensure_dirs():
    for d in (DATA_DIR, MODELS_DIR, RESULTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
