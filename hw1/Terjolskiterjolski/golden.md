# HW1 - Three golden questions

**Nikolozi Kutaladze (Terjolskiterjolski) | Run: 20 October 2026, Tbilisi**

Synthetic inputs live in `src/data/listings.json`. Run from the repository root:
```sh
python hw1/Terjolskiterjolski/src/run_golden.py
python -m pytest hw1/Terjolskiterjolski -q
```

The runner compares full result objects, prints expected and actual outputs, and exits nonzero if any differ. The captured run is in `src/evidence/golden-results.json`; the test summary is in `src/evidence/pytest-results.txt`.

| # | Question / input | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Find `calculator` within `Electronics`. | Only `calc-1`; exclude the matching Books study guide. Reason: `Matched title terms: calculator.` | `[{"listing_id": "calc-1", "reason": "Matched title terms: calculator."}]` | PASS |
| 2 | Find `chemistry textbook` within `"  bOoKs  "`. | `book-chem`, then `book-physics`; exclude the Electronics reader. Normalize whitespace/case without changing relevance. | `[{"listing_id": "book-chem", "reason": "Matched title terms: chemistry, textbook."}, {"listing_id": "book-physics", "reason": "Matched title terms: textbook."}]` | PASS |
| 3 | Find `calculator` within `Transport`, where there are no indexed listings. | `[]`; never fall back to calculators in another category. | `[]` | PASS |

All three cases were run against the implementation, not inferred from expected results. The full test run passed **20 tests and 6 subtests**: ten inherited baseline tests and ten new tests. Extra checks include blank/invalid categories, exact versus substring matching, no keyword overlap, compatibility without a filter, changed categories, removal, ties, and CLI output/error handling. Runtime model calls, tokens and model cost are all zero; this does not measure the coding assistant's usage.
