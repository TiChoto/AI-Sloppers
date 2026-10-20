# HW1 spec — Local keyword search for UniMarket

*Ti_Choto · UniMarket · individual feature. From the repository root: `python -m pip install -r hw1/Ti_Choto/src/requirements.txt && pytest hw1/Ti_Choto`. The search code itself uses only the Python standard library.*

## Goal and users

Give students a small, predictable natural-language search path over the listings already indexed by UniMarket. A student can ask for an item in ordinary words; the assistant returns matching listing IDs in relevance order and a short reason grounded in listing fields. This is a local keyword baseline for the team’s `SearchAssistant` contract, which currently has an interface but no implementation.

## Acceptance criteria

1. `LocalKeywordSearch.index_listing(listing)` indexes `id`, `title`, `description`, `category`, and `condition`; indexing the same ID again replaces its previous entry.
2. `query(text)` returns an empty list for blank input or when no indexed listing shares a meaningful query token.
3. Matching is case-insensitive and ignores punctuation. Common function words (`a`, `an`, `the`, `for`, `to`, `in`, `on`, `of`, `and`, `or`, `i`, `me`, `my`, `with`, `please`, `looking`, `find`, `want`, `need`) are ignored. Tokens in the title score 4, category 3, condition 2, and description 1; each query token contributes only its highest matching field score.
4. Results are ordered by score descending, then title and ID ascending (case-insensitive title); each ID appears at most once. Only indexed IDs can be returned.
5. Every result includes a concise reason listing the matched query terms and the fields they matched. The reason does not claim price or other facts that this feature did not search.
6. Re-indexing an ID updates later results; removing an ID prevents it from appearing. Removing an unknown ID is a no-op. No model, network, database, or environment key is used.

## Context and boundaries

Context: `hw1/LashaJaparidze/src/draftcheck/` is the latest individual feature snapshot supplied for UniMarket; `hw1/LukaVasadze07/src/unimarket/assistants/search_assistant.py` defines the team search interface; `hw1/LukaVasadze07/src/unimarket/listings/model.py` defines listing fields. This HW1 implements the missing local search behavior in its own folder and does not edit either teammate’s slice.

Out of scope: embeddings, synonyms, model calls, price understanding, HTTP routes, persistence, and changes to the shared app. Results are lexical matches, not semantic guarantees. Estimated cost is $0 per query; token use is zero.
