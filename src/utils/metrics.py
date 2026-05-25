"""Metrics placeholders for staged research development."""

from __future__ import annotations


def accuracy(pred, target):
    correct = (pred == target).sum()
    total = target.size
    return float(correct / total)
