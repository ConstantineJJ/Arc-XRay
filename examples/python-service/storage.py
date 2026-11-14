"""Demonstration persistence boundary with a deliberately cyclic import."""
import service
from pathlib import Path


def pending():
    return []


def save(result):
    Path("result.txt").write_text(str(result), encoding="utf-8")
