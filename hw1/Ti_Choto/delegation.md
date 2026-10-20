# HW1 delegation log · PriceCheck

> DRAFT: edit this to match what you actually did and decided. Fill in the rung yourself.

### Entry 1 · Build PriceCheck feature
- **Task:** Acceptance criteria 1 to 5 in `spec.md`.
- **Delegated to:** Claude (chat, no repo access). Context given: the course brief for HW1 and the shape of the UniMarket listing model (condition values, 2-decimal prices). Rung: **[fill in]**.
- **Plan check:** [fill in: what you changed or approved before building, e.g. you chose the ±30% band and the 3-comparable minimum]
- **Came back wrong:** Nothing in the first run. What was checked: (a) the 19 tests passed; (b) I changed `amount < fair_min` to `<=` on purpose and the test `test_band_edges_are_inclusive` failed, so the boundary test can fail; (c) the four CLI runs in `golden.md` matched expectations. Limitation: the tool could not install pytest, so the first run used a small stand-in runner. **[Replace with your own `pytest hw1/Ti_Choto` result from your machine.]**
- **Caught by:** running tests and a deliberate break of the boundary.
- **Decision:** kept as is.
- **AGENTS.md change:** none needed.
- **Cost:** [fill in: minutes]
