#!/usr/bin/env python3
"""Portable launcher; supports execution from any working directory."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "skills/arc-xray/scripts"))

from arc_xray.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
