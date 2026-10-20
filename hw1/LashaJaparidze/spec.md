# HW1 spec · DraftCheck: route an AI listing draft before the seller sees it

*Lasha Japaridze · GitHub `LashaJaparidze` · UniMarket · one page. From the repo root: `pip install -r hw1/LashaJaparidze/src/requirements.txt && pytest hw1/LashaJaparidze` · Try it: `cd hw1/LashaJaparidze/src && python -m draftcheck examples/clean.json`*

## Goal

UniMarket's listing assistant will turn a seller's rough text (and later a photo) into a draft with `title`, `category`, `condition` and `price`, each as `{value, evidence, confidence}`. DraftCheck is the pure `decide()` that runs on that draft **before** the seller sees the form. It answers one question: which fields can be prefilled, and which must the seller type themselves? It is the mitigation for the Design Review risk I am contact for: *the model invents a brand, condition or price*.

## Users

A student selling a used item, who sees the prefilled form. Later, the team's listing assistant calls `decide()` on every draft.

## Acceptance criteria

`decide(draft, seller_text)` returns `route`, `flags` (flag, field, reason), `hard` (fields) and `form` (field → value to prefill, or `null`). Text matching is case-insensitive and ignores repeated whitespace.

1. **accepted.** Every field has a non-blank value, evidence that appears in `seller_text`, confidence ≥ 0.6; `condition` is one of `new`, `like_new`, `good`, `fair`, `poor`; `price` is a non-negative amount with at most 2 decimals and equals a number in its evidence. Then `flags` and `hard` are empty and `form` holds all four values, price as `"25.00"`. `accepted` publishes nothing: the seller still presses Publish.
2. **review (hard flags).** `missing` (value null or blank), `no_evidence` (evidence null or blank), `price_not_in_text` (price evidence not in `seller_text`: a price is never taken from a photo), `invalid_price`, `price_mismatch`, `invalid_condition`. Each flagged field is in `hard` and its `form` value is `null`, never the model's value. Evidence is checked before confidence: no evidence at confidence 0.99 is still hard.
3. **confirm (soft flags only).** `not_in_text` (title, category or condition evidence not in `seller_text`, e.g. read from a photo) and `low_confidence` (< 0.6). Every value is prefilled; `hard` is empty.
4. **rejected.** All four values are null: `form` is all `null` and the message asks the seller to describe the item, its condition and price.
5. **Error case.** CLI input that fails the schema (a field missing, confidence outside 0 to 1, a non-string value, no `seller_text`) or an unreadable file: `error: ...` on stderr, nothing on stdout, exit code 2. Valid input: one JSON object on stdout, exit 0.
6. **Cost and latency.** No network, no model call, no file access inside `decide()`; it does not change its input. 1,000 calls take under 1 second.

## Context the agent needs

This file; `src/draftcheck/` and `src/tests/`; `Lab-3/examples/poster-extraction/src/checks.py` and `Lab-3/resources/confidence-signals.md` (the `decide()` pattern); condition values from Luka's listing model (`hw1/LukaVasadze07/src/unimarket/listings/model.py`), read only; `docs/DESIGN-REVIEW.md` section 3, risk 1.

## Constraints

Python 3.11+, `pydantic` and `pytest` only. Money is `Decimal`, never float. Values are strings or null. Thresholds live in named constants in `checks.py`.

## Out of scope

The model call that produces the draft, image handling, the seller form UI, saving or publishing a listing, prices in words ("twenty lari"), thousands separators ("1,200" goes to review), other languages.

## Napkin math

DraftCheck itself costs $0 per draft. The upstream text draft it guards, estimated (not measured): ~400 input + ~150 output tokens at the course price table for `google/gemini-3.8-flash` ($0.75 / $3.75 per million) ≈ $0.0009 per draft; the Design Review's 600 drafts a month ≈ $0.53.

## Verification

Green = `pytest hw1/LashaJaparidze` passes with no API key. The three golden questions in `golden.md` run with `python -m draftcheck examples/<file>.json`.
