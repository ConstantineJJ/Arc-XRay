#!/usr/bin/env python3
"""Self-contained skill entrypoint; no server or project-specific tools required."""
import sys

sys.dont_write_bytecode = True

from arc_xray.__main__ import main

if __name__ == "__main__":
    raise SystemExit(main())
