"""Put this folder first on sys.path so `import pricecheck` works from the repo root."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
