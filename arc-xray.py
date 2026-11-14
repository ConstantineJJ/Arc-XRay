#!/usr/bin/env python3
"""Portable launcher; supports execution from any working directory."""
import sys

sys.dont_write_bytecode = True

from arc_xray.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
