"""Price sanity check for a draft UniMarket listing.

Pure Python, no network, no model call. Compares a draft price with the
median price of comparable listings (same category, same condition).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from statistics import median

CONDITIONS = ("new", "like_new", "good", "fair", "poor")
MIN_COMPARABLES = 3
BAND = Decimal("0.30")  # fair = within 30% of the median, inclusive


@dataclass(frozen=True)
class Comparable:
    """A listing already on the market, reduced to what the check needs."""

    category: str
    condition: str
    price: Decimal


@dataclass(frozen=True)
class PriceVerdict:
    verdict: str  # "low" | "fair" | "high" | "insufficient_data"
    median: Decimal | None
    count: int  # how many comparables were actually used
    fair_min: Decimal | None
    fair_max: Decimal | None


def parse_price(value: object) -> Decimal:
    """Non-negative price with at most 2 decimals. Raises ValueError otherwise."""
    if isinstance(value, bool) or value is None:
        raise ValueError("price must be a non-negative number with at most 2 decimal places")
    try:
        amount = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError("price must be a non-negative number with at most 2 decimal places") from exc
    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal("0.01")):
        raise ValueError("price must be a non-negative number with at most 2 decimal places")
    return amount.quantize(Decimal("0.01"))


def check_price(
    category: str, condition: str, price: object, comparables: list[Comparable]
) -> PriceVerdict:
    """Return a verdict for the draft price.

    Comparables match on category (case-insensitive, trimmed) and condition
    (exact). With fewer than MIN_COMPARABLES matches the verdict is
    "insufficient_data" and no median is reported.
    """
    if not isinstance(category, str) or not category.strip():
        raise ValueError("category must be non-empty text")
    if condition not in CONDITIONS:
        raise ValueError(f"condition must be one of: {', '.join(CONDITIONS)}")
    amount = parse_price(price)

    wanted = category.strip().casefold()
    prices = [
        c.price
        for c in comparables
        if c.category.strip().casefold() == wanted and c.condition == condition
    ]
    if len(prices) < MIN_COMPARABLES:
        return PriceVerdict("insufficient_data", None, len(prices), None, None)

    mid = Decimal(median(prices)).quantize(Decimal("0.01"))
    fair_min = (mid * (1 - BAND)).quantize(Decimal("0.01"))
    fair_max = (mid * (1 + BAND)).quantize(Decimal("0.01"))
    if amount < fair_min:
        verdict = "low"
    elif amount > fair_max:
        verdict = "high"
    else:
        verdict = "fair"
    return PriceVerdict(verdict, mid, len(prices), fair_min, fair_max)
