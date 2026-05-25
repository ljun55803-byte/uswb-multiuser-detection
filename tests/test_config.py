from __future__ import annotations

from pathlib import Path

from src.config import load_config


def test_derived_parameters() -> None:
    cfg = load_config(Path("configs/default.yaml"))

    assert cfg["symbol_samples"] == 1024
    assert cfg["pulse_samples"] == 64
    assert cfg["ppm_shift_samples"] == 100
    assert cfg["min_space_samples"] == 64
    assert cfg["max_space_samples"] == 300
