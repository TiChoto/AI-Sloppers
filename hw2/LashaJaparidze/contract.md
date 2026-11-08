# Tool Contract: validate_listing_draft

## Schema Rules
- Strict Pydantic validation enabled with `extra = "forbid"`.
- `title`: Non-empty string, maximum 100 characters.
- `price`: Decimal greater than or equal to 0.00.
- `condition`: Must be one of `new`, `like_new`, `good`, `fair`, or `poor`.

## Session Identity Locking
- Seller identity (`user_id`) is retrieved strictly from the active session context.
- Function arguments NEVER accept `user_id`, `seller_id`, or `student_id` to prevent parameter spoofing.
