"""Offline demo: python -m unimarket 'calculator' --category Books."""

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

from unimarket.assistants.local_search import LocalKeywordSearch


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    parser.add_argument("--category", default=None)
    parser.add_argument(
        "--data", type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "listings.json",
    )
    args = parser.parse_args()
    search = LocalKeywordSearch()
    try:
        for record in json.loads(args.data.read_text(encoding="utf-8")):
            search.index_listing(SimpleNamespace(**record))
        results = search.query(args.query, category=args.category)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        parser.error(str(exc))
    print(json.dumps([asdict(result) for result in results], ensure_ascii=False))


if __name__ == "__main__":
    main()
