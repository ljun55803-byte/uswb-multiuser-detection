"""Nakagami channel placeholder."""

from __future__ import annotations

import numpy as np


def fading_coefficients(num_paths: int, m: float, omega: float) -> np.ndarray:
    if num_paths <= 0:
        raise ValueError("num_paths must be positive")
    scale = np.sqrt(omega / (2.0 * m))
    return np.random.gamma(shape=m, scale=scale, size=num_paths)
