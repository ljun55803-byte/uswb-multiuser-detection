"""TH-PPM functions."""

from __future__ import annotations


class SimpleArray(list):
    @property
    def shape(self):
        return (len(self),)


def modulate_th_ppm(bits, th_code, cfg, pulse):
    bits = [int(b) for b in bits]
    th_code = [int(c) for c in th_code]

    num_symbols = int(cfg.num_symbols)
    symbol_samples = int(cfg.symbol_samples)
    chip_samples = int(cfg.chip_samples)
    ppm_shift_samples = int(cfg.ppm_shift_samples)
    pulse_samples = int(cfg.pulse_samples)

    if len(bits) != num_symbols or len(th_code) != num_symbols:
        raise ValueError("bits and th_code must have length num_symbols")

    x = [0.0] * (num_symbols * symbol_samples)
    pulse_positions = [0] * num_symbols

    for n in range(num_symbols):
        base = n * symbol_samples + th_code[n] * chip_samples
        pos = base if bits[n] == 0 else base + ppm_shift_samples
        end = pos + pulse_samples
        if pos < 0 or end > len(x):
            raise ValueError(f"pulse index out of range at symbol {n}: [{pos}, {end})")
        for i in range(pulse_samples):
            x[pos + i] += float(pulse[i])
        pulse_positions[n] = pos

    return SimpleArray(x), SimpleArray(pulse_positions)
