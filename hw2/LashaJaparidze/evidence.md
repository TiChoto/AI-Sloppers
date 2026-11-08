# HW2 Evidence: validate_listing_draft

## CI Enforcement
- **Red CI Run (Blocked Merge)**: Verified locally / on feature branch by deliberately relaxing contract constraints (e.g. allowing empty titles or negative prices), resulting in failing test cases and GitHub Actions blocking the pull request.
- **Green CI Run (Successful Merge)**: Verified with strict schema validation (`extra = "forbid"`, positive price constraints, valid condition enums), passing all 5 golden eval cases in `evals/tools/LashaJaparidze.yaml`.

## Golden Eval Cases Summary
- **Case 1 (Valid Input)**: Standard item listing with valid title, price, and condition. Pass.
- **Case 2 (Boundary Price)**: Listing with $0.00 price (free item). Pass.
- **Case 3 (Invalid Condition)**: Listing with unrecognized condition string. Fails as expected.
- **Case 4 (Negative Price)**: Listing with price < 0. Fails as expected.
- **Case 5 (Adversarial Parameter Spoofing)**: Input attempting to pass explicit `user_id` or `seller_id` parameters. Fails validation due to `extra = "forbid"`.
