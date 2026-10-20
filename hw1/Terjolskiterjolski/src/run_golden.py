"""Run three golden cases and print machine-readable actual results."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from unimarket.assistants.local_search import LocalKeywordSearch


def main():
    search = LocalKeywordSearch()
    for record in json.loads((Path(__file__).parent / "data/listings.json").read_text(encoding="utf-8")):
        search.index_listing(SimpleNamespace(**record))
    cases = [
        ("calculator", "Electronics", [
            {"listing_id": "calc-1", "reason": "Matched title terms: calculator."}]),
        ("chemistry textbook", "  bOoKs  ", [
            {"listing_id": "book-chem", "reason": "Matched title terms: chemistry, textbook."},
            {"listing_id": "book-physics", "reason": "Matched title terms: textbook."}]),
        ("calculator", "Transport", []),
    ]
    results = []
    for query, category, expected in cases:
        actual = [asdict(r) for r in search.query(query, category=category)]
        results.append(dict(query=query, category=category, expected=expected,
                            actual=actual, passed=actual == expected))
    print(json.dumps(dict(run_at_utc=datetime.now(timezone.utc).isoformat(),
                          model_calls=0, tokens=0, cost_usd=0, results=results), indent=2))
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
