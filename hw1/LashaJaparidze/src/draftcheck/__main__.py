"""Run decide() on one JSON file and print the decision.

Usage:  python -m draftcheck examples/clean.json
Exit 0 with one JSON object on stdout; exit 2 with `error: ...` on stderr.
"""

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from .checks import decide
from .draft import DraftInput


def _describe(exc: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(str(p) for p in err['loc']) or 'input'}: {err['msg']}" for err in exc.errors()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m draftcheck", description=__doc__.splitlines()[0])
    parser.add_argument("input", help="JSON file with seller_text and draft")
    args = parser.parse_args(argv)
    try:
        data = DraftInput.model_validate_json(Path(args.input).read_bytes())
    except OSError as exc:
        print(f"error: cannot read {args.input}: {exc.strerror}", file=sys.stderr)
        return 2
    except ValidationError as exc:
        print(f"error: invalid input: {_describe(exc)}", file=sys.stderr)
        return 2
    print(json.dumps(decide(data.draft, data.seller_text).to_json(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
