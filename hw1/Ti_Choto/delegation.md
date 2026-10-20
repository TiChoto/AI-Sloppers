# HW1 delegation log — Local UniMarket search

**Date:** 2026-10-20 · **Delegated to:** Codex coding assistant · **Autonomy Ladder:** rung 4 (implementation and tests drafted from the task; human review and run required).

I asked the assistant to inspect the supplied UniMarket HW1 snapshot, identify a small feature that the app contract still lacks, and build it inside `hw1/Ti_Choto/`. It proposed a deterministic keyword implementation of the existing `SearchAssistant` interface. The existing search protocol was a contract only: it required indexing, removal, ranked IDs, explanations, and empty results for blank input, but had no implementation. The feature stays local and has no model call.

**What came back wrong:** the first pass copied Lasha’s existing DraftCheck folder as if I wanted that same feature. That did not meet my request for a new feature. I caught it and clarified before the deliverable docs were written. I removed those copied files from the output and used them only as context; the final feature is a new local search implementation. I also kept Lasha’s and Luka’s folders read-only.

**How I checked it:** compared the implementation plan with Luka’s `SearchAssistant` protocol; ran all three golden queries directly and ran the ten-test suite with Python’s standard `unittest` runner. `pytest` is declared in `src/requirements.txt`, but was not installed in this workspace, so the exact course pytest command remains to be run after installing that requirement. I reviewed that indexing replacement, removal, ranking, and explanations all have assertions. Any remaining limitation is stated in the spec: lexical token overlap does not understand synonyms or price intent.

**Decision:** keep the feature as a standalone slice under `hw1/Ti_Choto/`; later integration into the shared app should happen through the normal team review process. No API key or model tokens were used.
