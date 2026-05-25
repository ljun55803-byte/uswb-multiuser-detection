from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config


if __name__ == "__main__":
    cfg = load_config(PROJECT_ROOT / "configs" / "default.yaml")
    keys = [
        "ts",
        "symbol_samples",
        "pulse_samples",
        "ppm_shift_samples",
        "min_space_samples",
        "max_space_samples",
    ]
    for k in keys:
        print(f"{k}: {cfg[k]}")
