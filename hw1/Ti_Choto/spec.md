# HW1 spec · UniMarket PriceCheck

*Ti_Choto · one page. From the repo root: `pytest hw1/Ti_Choto` (Python 3.11+, no packages to install except pytest). Run it: `cd hw1/Ti_Choto/src && python -m pricecheck --category Home --condition good --price 11 --comparables data/sample_comparables.json`*

## Goal
Before a student publishes a UniMarket listing, tell them whether their asking price is **low**, **fair**, or **high** compared with similar listings. Stand-alone: it takes the comparables as input and does not import the listings service.

## Users
A student drafting a second-hand listing; later, the listing form or Member 2's assistant can call it.

## Acceptance criteria
1. `check_price(category, condition, price, comparables)` uses only comparables with the same category (case-insensitive, trimmed) and the exact same condition.
2. With 3 or more matches it returns the median (2 decimals) and a fair range of median ±30%, bounds inclusive. Price below the range is `low`, above is `high`, otherwise `fair`. Example: comparables 8, 10, 12 give range 7.00 to 13.00; 7.00 and 13.00 are `fair`, 6.99 is `low`, 13.01 is `high`.
3. With fewer than 3 matches it returns `insufficient_data`, `median` null, and `count` set to the matches found.
4. Error cases raise `ValueError`: price negative, non-numeric, NaN or infinite, boolean, null, or more than 2 decimal places; condition not one of `new`, `like_new`, `good`, `fair`, `poor`; blank category.
5. The CLI prints one JSON object and exits 0. On invalid input it prints `error: ...` to stderr, prints nothing to stdout, and exits 2.

## Context the agent needs
`src/pricecheck/check.py`, `src/pricecheck/__main__.py`, `src/tests/`. Condition values match the UniMarket listing model.

## Constraints
No model call, no API key, no network. Money uses `Decimal`, never float.

## Out of scope
HTTP endpoint, reading live listings, per-category ranges, currency, outlier removal.

## Verification
`pytest hw1/Ti_Choto` green; the four runs in `golden.md`.
