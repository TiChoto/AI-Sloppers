# Evaluation Golden Set

| ID | Test Input | Expected Output / Behavior | Category |
|---|---|---|---|
| Q1 | Valid listing: price = 30, title = "Calculus Book" | HTTP 200 / Created listing object with ID | Factual |
| Q2 | Invalid listing: price = -10 | HTTP 422 / Unprocessable Entity (Price must be > 0) | Edge Case |
| Q3 | Empty title or description | HTTP 422 / Validation Error | Refusal |
