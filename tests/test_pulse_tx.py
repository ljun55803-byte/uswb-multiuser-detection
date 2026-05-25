from __future__ import annotations

from pathlib import Path

from src.config import load_config
from src.tx.pulse import gaussian_second_derivative_pulse
from src.tx.th_ppm import modulate_th_ppm


def test_pulse_and_tx_properties() -> None:
    cfg = load_config(Path("configs/default.yaml"))

    pulse = gaussian_second_derivative_pulse(cfg)
    assert pulse.shape[0] == 64
    energy = sum(v * v for v in pulse)
    assert abs(energy - 1.0) < 1e-8

    assert cfg["chip_samples"] == 128

    bits = [0] * cfg.num_symbols
    th_code = [0] * cfg.num_symbols
    x, pulse_positions = modulate_th_ppm(bits, th_code, cfg, pulse)

    assert x.shape[0] == cfg.num_symbols * cfg.symbol_samples
    assert all(pos >= 0 for pos in pulse_positions)
    assert all(pos + cfg.pulse_samples <= x.shape[0] for pos in pulse_positions)
