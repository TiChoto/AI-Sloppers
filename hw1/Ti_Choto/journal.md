# Pattern Journal — Ti_Choto — Weeks 1 to 4

*AI-assisted retrospective draft based on the supplied course materials and this HW1 implementation. Edit the personal reflection wording to match what you actually did or observed in each teaching week before submitting; no personal Week 1–4 journal was included in the supplied archives.*

## Week 1 — Context as Budget

For this feature, the useful context was the team’s `SearchAssistant` protocol and the shared listing fields. I kept the implementation limited to indexed title, description, category, and condition text. The Lasha DraftCheck snapshot provided current UniMarket context, but did not need to be copied into the feature. I would do differently: confirm the intended feature before starting implementation so I do not spend effort reproducing an existing slice.

## Week 2 — Spec Before Code

I translated the search protocol into criteria that tests can decide: exact weighting, tie-breaking, empty input, replacement, removal, and output explanations. This made “natural language search” concrete as a deliberately small lexical baseline. I would do differently: decide the stopword and tokenization behavior even earlier and include those examples in the first spec draft.

## Week 3 — Uncertainty-Aware UX

The search assistant explains which query terms matched which listing fields. That gives a student evidence for a result without implying the system understood synonyms or price intent. I would do differently: ask a student to review whether these explanations are useful before connecting the slice to the app UI.

## Week 4 — Grounded Generation

This feature does not generate text with a model. Its reason strings are assembled from actual token matches in indexed fields, so they cannot invent a match. The golden set checks one specific query, one color-versus-title ranking, and one specific-versus-general textbook match. I would do differently: add a future golden case for a misspelling before claiming the search handles that behavior; this implementation does not.
