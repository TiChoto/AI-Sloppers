"""Put this folder on sys.path so `import unimarket` loads the HW1 copy.

The store root also contains a `unimarket/` directory. Python can treat that
directory as a namespace package, which hides this copy. Tests import the
package next to this file.
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parent)
if _SRC in sys.path:
    sys.path.remove(_SRC)
sys.path.insert(0, _SRC)
