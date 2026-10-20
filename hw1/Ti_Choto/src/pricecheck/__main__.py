"""CLI: python -m pricecheck --category Home --condition good --price 12.50 --comparables file.json

The comparables file is a JSON list of {"category", "condition", "price"} objects.
Prints one JSON object. Exit code 2 and a message on stderr for invalid input.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal

from pricecheck.check import Comparable, check_price, parse_price


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="pricecheck")
    ap.add_argument("--category", required=True)
    ap.add_argument("--condition", required=True)
    ap.add_argument("--price", required=True)
    ap.add_argument("--comparables", required=True, help="path to a JSON list")
    args = ap.parse_args(argv)
    try:
        with open(args.comparables, encoding="utf-8") as fh:
            rows = json.load(fh)
        comps = [Comparable(r["category"], r["condition"], parse_price(r["price"])) for r in rows]
        v = check_price(args.category, args.condition, args.price, comps)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    out = {k: (f"{x:.2f}" if isinstance(x, Decimal) else x) for k, x in v.__dict__.items()}
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
