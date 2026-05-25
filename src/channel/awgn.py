"""AWGN channel placeholder."""

from __future__ import annotations

import numpy as np


def add_awgn(x: np.ndarray, snr_db: float) -> np.ndarray:
    signal_power = np.mean(np.square(x)) + 1e-12
    snr_linear = 10 ** (snr_db / 10.0)
    noise_power = signal_power / snr_linear
    noise = np.random.normal(0.0, np.sqrt(noise_power), size=x.shape)
    return x + noise
