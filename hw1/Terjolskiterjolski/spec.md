# HW1 - Category-filtered UniMarket search

**Nikolozi Kutaladze | GitHub: Terjolskiterjolski | 20 October 2026**

From the repository root (Python 3.10+):
```sh
python -m pip install -r hw1/Terjolskiterjolski/src/requirements.txt
python -m pytest hw1/Terjolskiterjolski -q
python hw1/Terjolskiterjolski/src/run_golden.py
cd hw1/Terjolskiterjolski/src
python -m unimarket calculator --category Electronics
```

## Goal and users

Students shopping on UniMarket need to search within a chosen category. A search for "calculator" in Electronics should return a calculator, without a study guide in Books. Add one optional category filter to the latest Ti_Choto local-search baseline. The filter narrows candidates; the existing ranker and evidence explanations determine their order. The standalone CLI demonstrates the feature with synthetic listings.

## Acceptance criteria

1. `LocalKeywordSearch.query(text, category=None)` retains the baseline results and explanations when the category is omitted or `None`; existing one-argument callers continue to work.
2. A supplied category matches the listing category exactly after `strip().casefold()` on both sides. `"  bOoKs  "` matches Books; `"Book"` does not. Filtering uses the stored category, never title/description mentions.
3. Only listings in the selected category may appear. Unknown categories return `[]`; there is no fallback to other categories. A category alone does not create a keyword match; blank/no-match queries return `[]`.
4. Preserve baseline token scoring: title 4, category 3, condition 2, description 1; each distinct query token scores its strongest field only. Sort by descending score, then casefolded title and ID. Reasons name actual matched terms and fields; IDs are unique.
5. Reject a non-string, non-None category with `TypeError`; reject a whitespace-only category with `ValueError`, including for a blank query. Validate query text as in the baseline. The CLI prints JSON results, or exits 2 with a readable validation error.
6. Re-indexing an ID replaces its category and content; removing it hides it from later filtered queries. Tests cover these updates, deterministic ties, validation, the CLI and all three golden cases. No network/model calls or keys are needed.

## Context, ownership and boundaries

Baseline: `hw1/Ti_Choto/src/` at commit `782e26a`, the most recent existing HW1 slice. Its ranker and ten regression tests are copied and credited, not claimed as new work. New work: category filtering, CLI, synthetic fixtures, ten extension tests and golden runner. `hw1/LukaVasadze07/src/unimarket/assistants/search_assistant.py` supplies the shared search contract; its listing model defines category as free text. The Lab-3 milestone brief supplies the deliverable requirements.

Out of scope: full app integration, HTTP routes, UI, price filters, synonyms, embeddings, persistence and Design Review. Runtime model tokens/cost: 0 / $0. Test dependencies: pytest; application dependencies: standard library only. This folder runs independently of teammates' folders.
