"""Energy detector baseline placeholder."""

from __future__ import annotations

import numpy as np


def detect(x: np.ndarray, threshold: float) -> int:
    return int(np.sum(np.square(x)) > threshold)
