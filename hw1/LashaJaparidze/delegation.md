# HW1 delegation log · DraftCheck

**Date:** 2026-10-20 · **Tool:** Claude Code (desktop app), model Claude Opus 5.5 · **Rung on the Autonomy Ladder:** 4 in practice. One prompt, and the agent wrote the spec, tests, code and these files; my review came afterwards, on the diff, before the pull request.

### Entry 0 · the earlier draft of this folder
- **What was there:** a spec, golden set and log for `POST /listings/` with price validation, written with Gemini. The log says the endpoint was built, but the folder had no `src/` at all.
- **Came back wrong:** (1) The claim "built and verified" had nothing behind it. (2) The scope was Luka's HW1 (`hw1/LukaVasadze07`, listings CRUD with price validation), and HW1 must be my own feature. (3) Criteria like "HTTP 200 / Created listing object" did not match how the listing API actually answers (`201`).
- **Caught by:** reading the folder against the `Lab-3/MILESTONE-1.md` checklist and against Luka's folder.
- **Decision:** replaced. The new feature is DraftCheck, the mitigation for the risk I am contact for in `docs/DESIGN-REVIEW.md` §3: the model invents a brand, condition or price.

### Entry 1 · DraftCheck, spec to tests to code
- **Task:** AC1 to AC6 in `spec.md`.
- **Delegated:** "Read both repos, skip Ti_Choto's folder, do homework 1 fully for LashaJaparidze." The agent had the team repo, the course repo, and `Lab-3/examples/poster-extraction` as its reference.
- **Plan check:** the agent wrote `spec.md` first, then `tests/`, then `draftcheck/`. It added one rule beyond the Lab 3 reference: evidence must appear in the seller's text, and for price that is a hard flag.
- **Came back wrong:**
  1. **First test run: `1 failed, 28 passed`.** In `test_price_that_differs_from_its_evidence_is_hard`, the seller text the agent wrote said "barely used" but not "no highlights". The condition evidence therefore failed the text check, and an extra `not_in_text` flag appeared. The code was right and the test data was wrong. The test text was fixed; the assertion was not loosened.
  2. **A test that could not fail.** As a deliberate break, the order of the "evidence" and "confidence" checks in `checks.py` was swapped on a copy. The suite still said `29 passed`. The test used confidence 0.99, so the order made no difference. I added `test_evidence_is_checked_before_confidence` with confidence 0.2. The same break then gave `1 failed, 29 passed`.
  3. Two other deliberate breaks were caught at once. Treating a price from a photo as soft gave `2 failed`. Prefilling hard fields with the model's value gave `7 failed`.
- **Caught by:** running `pytest` myself, deliberate breaks on a throwaway copy of `src/`, and the three golden runs in `golden.md`.
- **Decision:** kept, after the two test fixes above. Final: `pytest hw1/LashaJaparidze` → `30 passed`; `pytest hw1` (all folders) → `110 passed`.
- **My own review of the diff:** _[Lasha: read `tests/` then `src/draftcheck/checks.py` before you open the PR. Write here what you checked and anything you changed.]_
- **AGENTS.md change:** the team repo has no `AGENTS.md` yet. The line I will propose: *never prefill a field `decide()` marked hard*.
- **Cost:** no model tokens in the feature. Setup took one extra step: Python was not installed on this machine, so the agent installed Python 3.12 (with my approval) before any test could run.
