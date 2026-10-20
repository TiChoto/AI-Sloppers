# HW1 spec · UniMarket listings

*Luka Vasadze · GitHub `LukaVasadze07` · one page. From the repo root: `pip install -r hw1/LukaVasadze07/src/requirements.txt && pytest hw1/LukaVasadze07`*

## Goal

A student saves a second-hand listing and finds it with structured filters. The service keeps listings in memory and supports create, retrieve, update, delete, and search over HTTP.

## Users

Students offering a used item, and students looking for one by words, category, and price. They send the field values themselves. This feature does not draft a listing.

## Acceptance criteria

1. `POST /listings` with title, description, category, price, condition, and optional `image_ref` returns `201` and all eight fields. The server assigns `id` and `created_at`. `GET /listings/{id}` returns the same JSON. Response `price` is a string with two decimal places.
2. `GET /listings` accepts optional `q`, `category`, `min_price`, and `max_price`, combined with AND. `q` is a case-insensitive substring of title or description. `category` is a case-insensitive exact match. Price bounds are inclusive. Results are newest `created_at` first.
3. `GET /listings?min_price=30&max_price=10` returns `422` and `{"detail":"min_price must not exceed max_price"}`. An invalid create body returns `422` and is not stored. An unknown id returns `404` and `{"detail":"Listing not found"}`.

## Context the agent needs

- `src/unimarket/listings/model.py`, `store.py`, `api.py`, and `src/unimarket/app.py`
- `src/tests/test_listing_model.py` and `src/tests/test_listings_api.py`
- The same contract in the foundation file `unimarket/docs/api.md`

## Constraints

Python 3.11 or newer. No API key. `condition` is exactly `new`, `like_new`, `good`, `fair`, or `poor`. `category` is free text. `image_ref` is a string or null, not file bytes. No model call, so token cost is not recorded.

## Out of scope

Member 2's AI Listing Assistant, Member 3's smart search and RAG, and Member 4's client. Those are a protocol or a boundary note, and they are not built here. Also out of scope: accounts, payments, delivery, upload, and a durable database.

## First slice

Criteria AC1, AC2, and AC3. Done when `pytest hw1/LukaVasadze07` is green and the three questions in `golden.md` pass. Not in this slice: an assistant implementation or a user interface.

## Verification

Green means the tests under `src/tests/` pass with no API key. The curl commands and the bodies they returned are in `golden.md`.

## Risks

Listings live in the process. Restarting it drops them. That is how this store works.
