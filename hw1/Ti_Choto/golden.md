# HW1 golden questions — UniMarket local search

Run from the repository root with `pytest hw1/Ti_Choto/src/tests/test_local_search.py -q`. The fixtures are handwritten and the assistant is deterministic; no model or network call is made. The exact query outputs below are produced by the golden tests.

| # | Question | Expected | Actual | Result and run |
|---|---|---|---|---|
| 1 | “I need a calculator for engineering exams” | The scientific calculator ranks first because “calculator” matches its title and “engineering” and “exams” match its description. | `['calc-1']`; reason: `Matched title terms: calculator; description terms: engineering, exams.` | Pass — `pytest hw1/Ti_Choto/src/tests/test_local_search.py::TestLocalKeywordSearch::test_engineering_calculator_query -q` |
| 2 | “blue bicycle” | Blue bicycle ranks ahead of a bicycle without a blue match; both remain visible, with the blue listing’s stronger evidence first. | `['bike-blue', 'bike-red']`; first reason: `Matched title terms: bicycle; description terms: blue.` Second: `Matched title terms: bicycle.` | Pass — `pytest hw1/Ti_Choto/src/tests/test_local_search.py::TestLocalKeywordSearch::test_blue_bicycle_ranks_color_evidence -q` |
| 3 | “looking for a chemistry textbook” | The chemistry textbook ranks first; a physics textbook with only “textbook” overlap ranks second; an unrelated laptop is absent. | `['book-chem', 'book-physics']`; first reason: `Matched title terms: chemistry, textbook.` Second: `Matched title terms: textbook.` | Pass — `pytest hw1/Ti_Choto/src/tests/test_local_search.py::TestLocalKeywordSearch::test_textbook_query_ranks_specific_match -q` |

I ran the three inputs directly against the implementation and confirmed the IDs and reasons shown above. The tests assert those same outputs against in-memory listings. The full suite also covers blank/no-match queries, duplicate replacement, removal, punctuation/case handling, deterministic ties, unique results, and the absence of an external model dependency.
