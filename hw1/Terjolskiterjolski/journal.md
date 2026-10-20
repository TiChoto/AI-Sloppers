# Pattern Journal - Nikolozi Kutaladze

**GitHub: Terjolskiterjolski | Weeks 1-4 | Recorded 20 October 2026**

These are AI-assisted retrospective reflections grounded in this HW1 session and the supplied course patterns. No earlier personal journal was available to copy. Week labels identify the course topics, not claims that these activities happened in those weeks; Nikolozi should confirm the reflections before submitting.

## Week 1 - Context as Budget
*Retrospective entry dated 20 October 2026.*

The useful context for this slice was Ti_Choto's local search, Luka's search contract and listing fields, and the HW1 brief. I delegated inspecting those sources to Codex; Git history verified the baseline rather than relying on an assumption that a folder was newest. Next time I would state the baseline commit and individual feature boundary at the start, so the agent spends less context on unrelated team work.

## Week 2 - Spec Before Code
*Retrospective entry dated 20 October 2026.*

"Search within a category" becomes testable when exact matching, whitespace/case normalization, unknown-category behavior and invalid input are explicit. I delegated the implementation and tests, then used exact result assertions and the inherited regression suite to check compatibility. Next time I would include the Books-versus-Electronics counterexample in the first task description so the acceptance condition is visible immediately.

## Week 3 - Uncertainty-Aware UX
*Retrospective entry dated 20 October 2026.*

An unknown category returns no results instead of silently relaxing the student's filter; a blank category is rejected rather than treated as unrestricted search. Codex implemented those boundaries, and tests checked both the Python errors and CLI exit status. Next time I would add a UI message explaining an empty result and offer an explicit user action to search all categories, while keeping the current API behavior predictable.

## Week 4 - Grounded Generation
*Retrospective entry dated 20 October 2026.*

This slice uses grounded retrieval without a generative model: every reason is assembled from terms that actually match indexed listing fields. I delegated a three-case golden runner and verified its actual JSON alongside tests that exclude keyword matches from the wrong category. Next time I would expand the evaluation with student-written queries and Georgian category names before claiming broader language coverage; the current golden set is a small synthetic check.
