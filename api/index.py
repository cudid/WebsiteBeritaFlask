import sys
from pathlib import Path

# Tambahkan root project ke path agar bisa import app & search_engine
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app  # noqa: E402
