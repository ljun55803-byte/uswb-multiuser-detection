from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class ConfigError(ValueError):
    """Raised when configuration is invalid."""


class Config(dict):
    """Dictionary with attribute-style access."""

    def __getattr__(self, item: str) -> Any:
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    __setattr__ = dict.__setitem__


def _parse_simple_yaml(text: str) -> Dict[str, Any]:
    cfg: Dict[str, Any] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ConfigError(f"Invalid config line: {raw_line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.lower() in {"true", "false"}:
            parsed: Any = value.lower() == "true"
        else:
            try:
                parsed = int(value)
            except ValueError:
                try:
                    parsed = float(value)
                except ValueError:
                    parsed = value
        cfg[key] = parsed
    return cfg


def _to_samples(value_seconds: float, ts: float) -> int:
    return int(round(value_seconds / ts))


def load_config(path: str | Path) -> Config:
    cfg = Config(_parse_simple_yaml(Path(path).read_text(encoding="utf-8")))

    fs = float(cfg["fs"])
    if fs <= 0:
        raise ConfigError("fs must be positive")

    ts = 1.0 / fs
    cfg["ts"] = ts

    cfg["symbol_samples"] = _to_samples(float(cfg["symbol_duration"]), ts)
    cfg["pulse_samples"] = _to_samples(float(cfg["pulse_width"]), ts)
    cfg["ppm_shift_samples"] = _to_samples(float(cfg["ppm_shift"]), ts)
    cfg["min_space_samples"] = _to_samples(float(cfg["min_space_ns"]) * 1e-9, ts)
    cfg["max_space_samples"] = _to_samples(float(cfg["max_space_ns"]) * 1e-9, ts)

    num_chips = int(cfg["num_chips"])
    if num_chips <= 0:
        raise ConfigError("num_chips must be positive")
    if cfg["symbol_samples"] % num_chips != 0:
        raise ConfigError("symbol_samples must be divisible by num_chips")
    cfg["chip_samples"] = cfg["symbol_samples"] // num_chips

    return cfg
