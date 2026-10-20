# Golden questions · PriceCheck

Run from `hw1/Ti_Choto/src` with `data/sample_comparables.json` (3 "Home / good" listings at 8, 10, 12; 2 "Electronics / good" at 150, 200). Outputs below are copied from real runs on 2026-10-20.

| # | Question (input) | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | Home, good, price 11: is it fair? | `fair`, median 10.00, range 7.00 to 13.00 | `{"verdict": "fair", "median": "10.00", "count": 3, "fair_min": "7.00", "fair_max": "13.00"}` | PASS |
| 2 | `home` (lowercase), good, price 30 | `high`, same median | `{"verdict": "high", "median": "10.00", "count": 3, "fair_min": "7.00", "fair_max": "13.00"}` | PASS |
| 3 | Electronics, good, price 175: only 2 comparables | `insufficient_data` | `{"verdict": "insufficient_data", "median": null, "count": 2, "fair_min": null, "fair_max": null}` | PASS |

Extra error check (not one of the three): price `-5` gives exit code 2 and `error: price must be a non-negative number with at most 2 decimal places` on stderr.

**How I ran them**
```
cd hw1/Ti_Choto/src
python -m pricecheck --category Home --condition good --price 11 --comparables data/sample_comparables.json
python -m pricecheck --category home --condition good --price 30 --comparables data/sample_comparables.json
python -m pricecheck --category Electronics --condition good --price 175 --comparables data/sample_comparables.json
```
