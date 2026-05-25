"""Matched filter baseline placeholder."""

from __future__ import annotations

import numpy as np


def correlate(x: np.ndarray, template: np.ndarray) -> np.ndarray:
    return np.correlate(x, template, mode="valid")
