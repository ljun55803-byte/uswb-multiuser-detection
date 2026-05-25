from __future__ import annotations

from pathlib import Path
import random
import struct
import sys
import zlib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_config
from src.tx.pulse import gaussian_second_derivative_pulse
from src.tx.th_ppm import modulate_th_ppm


def _save_signal_png(signal, path: Path, width: int = 1200, height: int = 300) -> None:
    canvas = [[255 for _ in range(width)] for _ in range(height)]
    sig_len = len(signal)
    x_idx = [int(i * (sig_len - 1) / (width - 1)) for i in range(width)]
    y_vals = [float(signal[i]) for i in x_idx]
    y_min, y_max = min(y_vals), max(y_vals)
    if y_max == y_min:
        y_norm = [0.5] * width
    else:
        y_norm = [(y - y_min) / (y_max - y_min) for y in y_vals]

    for col, val in enumerate(y_norm):
        row = int((height - 1) - val * (height - 1))
        row = max(0, min(height - 1, row))
        canvas[row][col] = 0

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw_rows = []
    for row in canvas:
        raw_rows.append(b"\x00" + bytes(row))
    raw = b"".join(raw_rows)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, level=9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


if __name__ == "__main__":
    cfg = load_config(PROJECT_ROOT / "configs" / "default.yaml")
    rng = random.Random(cfg.seed)

    bits = [rng.randint(0, 1) for _ in range(cfg.num_symbols)]
    th_code = [rng.randint(0, cfg.num_chips - 1) for _ in range(cfg.num_symbols)]
    pulse = gaussian_second_derivative_pulse(cfg)
    x, pulse_positions = modulate_th_ppm(bits, th_code, cfg, pulse)

    out_dir = PROJECT_ROOT / "results" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig_path = out_dir / "single_user_signal.png"
    _save_signal_png(x, fig_path)

    print("bits:", bits)
    print("th_code:", th_code)
    print("pulse_positions:", list(pulse_positions))
    print("x shape:", x.shape)
    print("saved figure:", fig_path)
