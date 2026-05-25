"""Transmit pulse utilities."""

from __future__ import annotations

import math


class SimpleArray(list):
    @property
    def shape(self):
        return (len(self),)


def gaussian_second_derivative_pulse(cfg):
    pulse_samples = int(cfg.pulse_samples)
    if pulse_samples <= 0:
        raise ValueError("pulse_samples must be positive")

    sigma = 0.25
    pulse = []
    for i in range(pulse_samples):
        t = -1.0 + 2.0 * i / pulse_samples
        gauss = math.exp(-(t * t) / (2.0 * sigma * sigma))
        val = ((t * t - sigma * sigma) / (sigma**4)) * gauss
        pulse.append(val)

    energy = sum(v * v for v in pulse)
    if energy <= 0:
        raise ValueError("invalid pulse energy")
    scale = math.sqrt(energy)
    return SimpleArray([v / scale for v in pulse])
