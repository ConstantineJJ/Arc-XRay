"""Synthetic intake service used to demonstrate source-backed architecture review.

This fixture is intentionally imperfect. Arc-XRay reads it; never run it as a service.
"""
from service import run

if __name__ == "__main__":
    run()
