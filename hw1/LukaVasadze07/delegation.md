# HW1 delegation log · UniMarket listings

**Date of this check:** 2026-10-20 · **Student:** Luka Vasadze (`LukaVasadze07`) · **Rung:** not recorded · **Tool that first wrote the foundation:** not recorded

**What this student owns.** The listings MVP: model (`id`, `title`, `description`, `category`, `price`, `condition`, `image_ref`, `created_at`), in-memory create/retrieve/update/delete, and structured search (`q`, `category`, `min_price`, `max_price`). Member 2's AI Listing Assistant and Member 3's smart search are protocols only. Member 4's client is a boundary note. None of those three is built.

**What was delegated.** Place that existing feature in `hw1/LukaVasadze07/src` so `pytest hw1/LukaVasadze07` runs it. Do not add a model, a UI, auth, payments, or delivery.

**What came back wrong.** (1) The first pytest stopped at collection: `ModuleNotFoundError: No module named 'unimarket.listings'` and `No module named 'unimarket.app'`. A `unimarket/` directory at the store root shadowed this copy. Caught by that run. `src/conftest.py` puts this folder first on `sys.path`. (2) The next run was `2 failed, 60 passed`. Both were `FileNotFoundError` for `.../src/src/unimarket/...`. The copied test still used the foundation paths. Caught by `test_listings_api_does_not_import_assistants` and `test_assistant_modules_do_not_import_fastapi`. The assertions are unchanged; the paths now point at `unimarket/` in this folder. The listing modules were not rewritten.

**How it was checked.** After that fix, `pytest hw1/LukaVasadze07 -p no:cacheprovider` reported `62 passed, 1 warning in 3.71s`. The three curl questions in `golden.md` were run on the foundation app first. A server started from this folder returned the same status codes. The fields checked on that second run are listed at the end of `golden.md`.

**Cost:** not recorded. This feature does not call a model.
