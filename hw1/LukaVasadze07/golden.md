# HW1 golden questions · UniMarket listings

Run on 20 October 2026 against the foundation app, a fresh process of `unimarket.app:app`, at `http://127.0.0.1:8765`. The store was empty at the start of each process. `id` and `created_at` are assigned by the server, so those two values are copied from the response rather than predicted.

Question 1 used the first process. Questions 2 and 3 used a second process, so the textbook id in question 2 is not the id from question 1.

| # | Question (input) | Expected | Actual | Pass? | How I ran it |
|---|---|---|---|---|---|
| 1 | `POST /listings` with the JSON below, then `GET /listings/{id}` | `201`, then `200` with the same body. Eight fields. `price` is `"20.00"`, `condition` is `"good"`, `image_ref` is `"photos/calculus"`, `created_at` ends in `Z`. | `201` in `0.046118` s, then `200` in `0.001980` s. Bodies equal. See below. | pass | `curl` commands below. Also covered by `src/tests/test_listings_api.py::test_create_and_retrieve`, inside the `62 passed` pytest run. |
| 2 | After three creates (textbook `20.00` / Textbooks, lamp `8.00` / Home, bike `60.00` / Transport), `GET /listings?q=calculus&category=Textbooks&min_price=10&max_price=25` | `200` and one listing: the textbook, price `"20.00"`, category `"Textbooks"`. | `200` in `0.001898` s. One object, the textbook below. Unfiltered list still had 3 titles: Bike, Lamp, Calculus textbook. | pass | `curl` below. `test_search_filters` asserts that `q=calculus` alone matches the textbook and the lamp; this question adds category and price, and the response was only the textbook. |
| 3 | `GET /listings?min_price=30&max_price=10` | `422` and `{"detail":"min_price must not exceed max_price"}` | `422` in `0.001439` s. Body: `{"detail":"min_price must not exceed max_price"}` | pass | `curl` below. Same assertion in `test_search_inverted_range_names_the_problem`. |

### Question 1 input

```json
{"title":"Calculus textbook","description":"No highlights","category":"Textbooks","price":"20.00","condition":"good","image_ref":"photos/calculus"}
```

```bash
curl -sS -w "\nhttp_code=%{http_code} time_total=%{time_total}\n" \
  -X POST http://127.0.0.1:8765/listings \
  -H 'content-type: application/json' \
  -d '{"title":"Calculus textbook","description":"No highlights","category":"Textbooks","price":"20.00","condition":"good","image_ref":"photos/calculus"}'
```

### Question 1 actual body (POST and GET were identical)

```json
{
    "id": "7617d1ae-9dff-492f-8fae-435b1ea43970",
    "title": "Calculus textbook",
    "description": "No highlights",
    "category": "Textbooks",
    "price": "20.00",
    "condition": "good",
    "image_ref": "photos/calculus",
    "created_at": "2026-10-20T17:37:46.669576Z"
}
```

### Question 2 actual body

Seeded in this order: textbook (`image_ref` null, price `"20.00"`), lamp (`"For late calculus problem sets"`, `"8.00"`, Home, fair), bike (`"City bike"`, `"60.00"`, Transport, good).

```bash
curl -sS -w "\nhttp_code=%{http_code} time_total=%{time_total}\n" \
  --get "http://127.0.0.1:8765/listings" \
  --data-urlencode "q=calculus" \
  --data-urlencode "category=Textbooks" \
  --data-urlencode "min_price=10" \
  --data-urlencode "max_price=25"
```

```json
[
    {
        "id": "0155e374-6fa0-4214-9554-814db41aca76",
        "title": "Calculus textbook",
        "description": "No highlights",
        "category": "Textbooks",
        "price": "20.00",
        "condition": "good",
        "image_ref": null,
        "created_at": "2026-10-20T17:37:58.652648Z"
    }
]
```

### Question 3 actual body

```bash
curl -sS -w "\nhttp_code=%{http_code} time_total=%{time_total}\n" \
  --get "http://127.0.0.1:8765/listings" \
  --data-urlencode "min_price=30" \
  --data-urlencode "max_price=10"
```

```json
{"detail":"min_price must not exceed max_price"}
```

### Pytest on the same code

Foundation, from `unimarket/` with `PYTHONPATH=src`: `62 passed, 2 warnings in 1.11s`. The warnings were a Starlette deprecation about `httpx`, and a cache write the store rejected (`Operation not permitted`). Neither changed the results.

`pytest hw1/LukaVasadze07 -p no:cacheprovider`, after the path fix in `delegation.md`: `62 passed, 1 warning in 3.71s`. The remaining warning is the Starlette deprecation.

A later process of this folder's code, on port `8766`, repeated the three requests. Question 1 returned `201` then `200`, with `price` `"20.00"`, `condition` `"good"`, `image_ref` `"photos/calculus"`, a 36-character id, a `created_at` ending in `Z`, and identical POST and GET bodies. Question 2 returned `200` and one row: title `"Calculus textbook"`, category `"Textbooks"`, price `"20.00"`. Question 3 returned `422` and the same `detail` string. The new ids and timestamps differed, which is what the server does. That second process had already stored the question 1 textbook, so its search row carried `image_ref` `"photos/calculus"` rather than the null from the foundation's question 2 seed.
