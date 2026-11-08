# Pattern Journal: HW2

## Week 5 Entry
- **Pattern**: Least Privilege Schema Enforcement
- **Used it**: Implemented `extra = "forbid"` and strict type/range constraints on `title`, `price`, and `condition` parameters in `validate_listing_draft`.
- **Do differently**: Define custom error messages for boundary violations to give clearer feedback during failure cases.

## Week 6 Entry
- **Pattern**: Session State
- **Used it**: Enforced retrieving `user_id` strictly from the active session context instead of allowing it as an explicit function argument to block parameter spoofing.
- **Do differently**: Add explicit logging for unauthenticated session attempts before rejecting the tool execution.

## Week 7 Entry
- **Pattern**: Defensive Input Validation & Golden Evals
- **Used it**: Added adversarial and boundary golden eval test cases in `evals/tools/LashaJaparidze.yaml` to verify CI blocks invalid tool calls.
- **Do differently**: Include additional evaluation cases testing string injection attacks within user-submitted text fields.
