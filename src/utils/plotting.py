"""Plotting utilities placeholders."""

from __future__ import annotations

import matplotlib.pyplot as plt


def plot_signal(x, title: str = "signal"):
    fig, ax = plt.subplots()
    ax.plot(x)
    ax.set_title(title)
    ax.set_xlabel("sample")
    ax.set_ylabel("amplitude")
    return fig, ax
