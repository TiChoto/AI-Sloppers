"""decide() against the acceptance criteria in spec.md. Hand-written drafts, no model."""

import time

from draftcheck.checks import REQUIRED, decide
from draftcheck.draft import Draft, Field


def f(value, evidence, confidence=0.9):
    return Field(value=value, evidence=evidence, confidence=confidence)


# AC1 · accepted

def test_clean_draft_is_accepted_and_fully_prefilled(clean, seller_text):
    d = decide(clean, seller_text)
    assert d.route == "accepted"
    assert d.flags == [] and d.hard == set()
    assert d.form == {
        "title": "Calculus textbook (Stewart, 8th edition)",
        "category": "Textbooks",
        "condition": "like_new",
        "price": "25.00",
    }


def test_price_is_normalised_to_two_decimals(clean, seller_text):
    clean.price = f("25", "25 GEL")
    d = decide(clean, seller_text)
    assert d.route == "accepted"
    assert d.form["price"] == "25.00"


def test_evidence_match_ignores_case_and_repeated_whitespace(clean, seller_text):
    clean.title = f("Calculus textbook", "CALCULUS   textbook")
    assert decide(clean, seller_text).route == "accepted"


# AC2 · review: hard fields are never prefilled

def test_invented_price_goes_to_review_with_price_blank(clean):
    text = "Casio fx-991EX calculator, works perfectly, small scratch on the cover. Photo attached."
    clean.title = f("Casio fx-991EX calculator", "Casio fx-991EX calculator")
    clean.category = f("Electronics", "calculator")
    clean.condition = f("good", "small scratch on the cover", 0.8)
    clean.price = f("45.00", "45 GEL", 0.9)  # the seller never wrote a price
    d = decide(clean, text)
    assert d.route == "review"
    assert d.flags == [("price_not_in_text", "price")]
    assert d.hard == {"price"}
    assert d.form["price"] is None
    assert d.form["title"] == "Casio fx-991EX calculator"


def test_missing_value_is_hard(clean, seller_text):
    clean.condition = f(None, None, 0.0)
    d = decide(clean, seller_text)
    assert d.route == "review"
    assert ("missing", "condition") in d.flags
    assert d.hard == {"condition"} and d.form["condition"] is None


def test_blank_value_counts_as_missing(clean, seller_text):
    clean.title = f("   ", "Calculus textbook")
    d = decide(clean, seller_text)
    assert ("missing", "title") in d.flags
    assert d.form["title"] is None


def test_no_evidence_is_hard_even_at_high_confidence(clean, seller_text):
    clean.category = f("Textbooks", None, 0.99)
    d = decide(clean, seller_text)
    assert d.route == "review"
    assert ("no_evidence", "category") in d.flags
    assert d.form["category"] is None


def test_evidence_is_checked_before_confidence(clean, seller_text):
    # No evidence and low confidence at once: unsupported beats unsure.
    # (With confidence 0.99 above, swapping the two checks went unnoticed.)
    clean.category = f("Textbooks", None, 0.2)
    d = decide(clean, seller_text)
    assert ("no_evidence", "category") in d.flags
    assert ("low_confidence", "category") not in d.flags
    assert d.route == "review" and d.form["category"] is None


def test_blank_evidence_counts_as_no_evidence(clean, seller_text):
    clean.condition = f("like_new", "  ")
    assert ("no_evidence", "condition") in decide(clean, seller_text).flags


def test_price_that_differs_from_its_evidence_is_hard(clean):
    text = "Calculus textbook (Stewart, 8th edition). Barely used, no highlights. 20 GEL"
    clean.price = f("25.00", "20 GEL")  # model "rounded up" the seller's price
    d = decide(clean, text)
    assert d.route == "review"
    assert d.flags == [("price_mismatch", "price")]
    assert d.form["price"] is None


def test_price_that_is_not_an_amount_is_hard(clean, seller_text):
    for bad in ("about 20", "-5", "25.999", "NaN"):
        clean.price = f(bad, "25 GEL")
        d = decide(clean, seller_text)
        assert ("invalid_price", "price") in d.flags, bad
        assert d.route == "review" and d.form["price"] is None


def test_condition_outside_the_listing_model_is_hard(clean, seller_text):
    clean.condition = f("Like New", "Barely used")
    d = decide(clean, seller_text)
    assert d.route == "review"
    assert ("invalid_condition", "condition") in d.flags
    assert d.hard == {"condition"}


def test_hard_and_soft_together_keep_soft_field_prefilled(clean, seller_text):
    clean.price = f(None, None, 0.0)
    clean.title = f("Calculus textbook", "Calculus textbook", 0.4)
    d = decide(clean, seller_text)
    assert d.route == "review"
    assert d.hard == {"price"}
    assert d.form["title"] == "Calculus textbook"  # soft: prefilled, highlighted by the UI


# AC3 · confirm

def test_evidence_from_the_photo_only_is_confirm(clean, seller_text):
    clean.category = f("Textbooks", "STEWART CALCULUS on the cover")
    d = decide(clean, seller_text)
    assert d.route == "confirm"
    assert d.flags == [("not_in_text", "category")]
    assert d.hard == set() and d.form["category"] == "Textbooks"


def test_low_confidence_alone_is_confirm(clean, seller_text):
    clean.condition = f("like_new", "Barely used", 0.55)
    d = decide(clean, seller_text)
    assert d.route == "confirm"
    assert d.flags == [("low_confidence", "condition")]
    assert d.form["condition"] == "like_new"


# AC4 · rejected

def test_nothing_item_like_is_rejected():
    empty = {n: f(None, None, 0.0) for n in REQUIRED}
    d =decide(Draft(**empty), "Does anyone know if the library is open on Sunday?")
    assert d.route == "rejected"
    assert d.form == {n: None for n in REQUIRED}


# Reasons and purity (AC6)

def test_every_flag_has_a_readable_reason(clean, seller_text):
    clean.price = f("25.00", None)
    clean.condition = f("like_new", "Barely used", 0.3)
    d = decide(clean, seller_text)
    out = d.to_json()
    assert len(out["flags"]) == len(d.flags)
    assert all(fl["reason"] and "_" not in fl["reason"] for fl in out["flags"])


def test_decide_does_not_change_its_input(clean, seller_text):
    clean.price = f("45.00", "45 GEL")
    before = clean.model_dump()
    decide(clean, "no price here")
    assert clean.model_dump() == before


def test_thousand_decisions_under_one_second(clean, seller_text):
    t0 = time.perf_counter()
    for _ in range(1000):
        decide(clean, seller_text)
    assert time.perf_counter() - t0 < 1.0
