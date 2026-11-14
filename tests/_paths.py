"""Load the same runtime distributed inside the standalone skill."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills/arc-xray/scripts"))
