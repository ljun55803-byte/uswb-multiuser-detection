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


def _save_signal_svg(signal, pulse_positions, path: Path, title: str, start: int = 0, end: int | None = None, width: int = 1200, height: int = 320) -> None:
    if end is None:
        end = len(signal)
    start = max(0, int(start))
    end = min(len(signal), int(end))
    if end <= start:
        raise ValueError("invalid plotting range")

    segment = [float(v) for v in signal[start:end]]
    y_min = min(segment)
    y_max = max(segment)
    if y_max == y_min:
        y_min -= 1.0
        y_max += 1.0

    margin_left = 70
    margin_right = 20
    margin_top = 35
    margin_bottom = 45
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    def sx(sample_idx: int) -> float:
        return margin_left + (sample_idx - start) * plot_w / max(1, (end - start - 1))

    def sy(val: float) -> float:
        return margin_top + (y_max - val) * plot_h / (y_max - y_min)

    points = []
    for i, v in enumerate(segment):
        px = sx(start + i)
        py = sy(v)
        points.append(f"{px:.2f},{py:.2f}")

    axis_y0 = sy(0.0) if y_min <= 0.0 <= y_max else margin_top + plot_h

    markers = []
    for p in pulse_positions:
        if start <= p < end:
            x = sx(int(p))
            markers.append(f'<line x1="{x:.2f}" y1="{margin_top}" x2="{x:.2f}" y2="{margin_top + plot_h}" stroke="#d62728" stroke-width="1" stroke-dasharray="4,3"/>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect x="0" y="0" width="{width}" height="{height}" fill="white"/>
  <text x="{width/2:.1f}" y="22" text-anchor="middle" font-family="Arial" font-size="16">{title}</text>
  <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="black" stroke-width="1"/>
  <line x1="{margin_left}" y1="{axis_y0:.2f}" x2="{margin_left + plot_w}" y2="{axis_y0:.2f}" stroke="black" stroke-width="1"/>
  {''.join(markers)}
  <polyline fill="none" stroke="#1f77b4" stroke-width="1.5" points="{' '.join(points)}"/>
  <text x="{width/2:.1f}" y="{height-10}" text-anchor="middle" font-family="Arial" font-size="13">sample index</text>
  <text x="16" y="{height/2:.1f}" transform="rotate(-90 16 {height/2:.1f})" text-anchor="middle" font-family="Arial" font-size="13">amplitude</text>
  <text x="{margin_left}" y="{height-28}" font-family="Arial" font-size="11">{start}</text>
  <text x="{margin_left + plot_w:.1f}" y="{height-28}" text-anchor="end" font-family="Arial" font-size="11">{end-1}</text>
</svg>
'''
    path.write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    cfg = load_config(PROJECT_ROOT / "configs" / "default.yaml")
    rng = random.Random(cfg.seed)

    bits = [rng.randint(0, 1) for _ in range(cfg.num_symbols)]
    th_code = [rng.randint(0, cfg.num_chips - 1) for _ in range(cfg.num_symbols)]
    pulse = gaussian_second_derivative_pulse(cfg)
    x, pulse_positions = modulate_th_ppm(bits, th_code, cfg, pulse)

    out_dir = PROJECT_ROOT / "results" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / "single_user_signal.png"
    _save_signal_png(x, png_path)

    docs_dir = PROJECT_ROOT / "docs" / "figures"
    docs_dir.mkdir(parents=True, exist_ok=True)
    full_svg_path = docs_dir / "single_user_signal_full.svg"
    zoom_svg_path = docs_dir / "single_user_signal_zoom.svg"

    _save_signal_svg(
        signal=x,
        pulse_positions=pulse_positions,
        path=full_svg_path,
        title="Single-user TH-PPM transmitted waveform",
        start=0,
        end=len(x),
    )

    zoom_start = int(pulse_positions[0]) - 50
    zoom_end = int(pulse_positions[0]) + int(cfg.pulse_samples) + 50
    _save_signal_svg(
        signal=x,
        pulse_positions=pulse_positions,
        path=zoom_svg_path,
        title="Zoomed Gaussian second-derivative pulse",
        start=zoom_start,
        end=zoom_end,
        width=900,
        height=320,
    )

    print("bits:", bits)
    print("th_code:", th_code)
    print("pulse_positions:", list(pulse_positions))
    print("x shape:", x.shape)
    print("saved png:", png_path)
    print("saved full svg:", full_svg_path)
    print("saved zoom svg:", zoom_svg_path)
