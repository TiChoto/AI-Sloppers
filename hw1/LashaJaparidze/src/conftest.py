"""Put this folder first on sys.path so `import draftcheck` works from the repo root.

Fixtures are hand-written drafts that stand in for what the listing
assistant model would return. No test in this folder calls a model.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from draftcheck.draft import Draft, Field  # noqa: E402

SELLER_TEXT = (
    "Selling my Calculus textbook (Stewart, 8th edition). "
    "Barely used, no highlights. 25 GEL, pick up at the KIU library."
)


def f(value, evidence, confidence=0.9):
    return Field(value=value, evidence=evidence, confidence=confidence)


@pytest.fixture
def seller_text():
    return SELLER_TEXT


@pytest.fixture
def clean():
    return Draft(
        title=f("Calculus textbook (Stewart, 8th edition)", "Calculus textbook (Stewart, 8th edition)", 0.95),
        category=f("Textbooks", "textbook"),
        condition=f("like_new", "Barely used, no highlights", 0.85),
        price=f("25.00", "25 GEL", 0.95),
    )
