from decimal import Decimal

import pytest

from pricecheck import Comparable, check_price


def comps(*prices, category="Home", condition="good"):
    return [Comparable(category, condition, Decimal(p)) for p in prices]


def test_fair_inside_band():
    v = check_price("Home", "good", "10.00", comps("8", "10", "12"))
    assert (v.verdict, v.median, v.count) == ("fair", Decimal("10.00"), 3)
    assert (v.fair_min, v.fair_max) == (Decimal("7.00"), Decimal("13.00"))


def test_band_edges_are_inclusive():
    c = comps("8", "10", "12")
    assert check_price("Home", "good", "7.00", c).verdict == "fair"
    assert check_price("Home", "good", "13.00", c).verdict == "fair"


def test_low_and_high_just_outside_band():
    c = comps("8", "10", "12")
    assert check_price("Home", "good", "6.99", c).verdict == "low"
    assert check_price("Home", "good", "13.01", c).verdict == "high"


def test_median_of_even_count():
    v = check_price("Home", "good", "10", comps("8", "10", "12", "20"))
    assert v.median == Decimal("11.00")


def test_category_is_case_insensitive_condition_is_exact():
    c = comps("8", "10", "12", category="home") + comps("1", "1", "1", condition="fair")
    v = check_price(" HOME ", "good", "10", c)
    assert v.count == 3 and v.median == Decimal("10.00")


def test_fewer_than_three_comparables_is_insufficient_data():
    v = check_price("Home", "good", "10", comps("8", "12"))
    assert (v.verdict, v.median, v.count, v.fair_min) == ("insufficient_data", None, 2, None)


def test_no_comparables_at_all():
    assert check_price("Home", "good", "10", []).verdict == "insufficient_data"


@pytest.mark.parametrize("bad", ["-1", "abc", "", "1.234", "NaN", "Infinity", True, None])
def test_invalid_price_rejected(bad):
    with pytest.raises(ValueError):
        check_price("Home", "good", bad, comps("8", "10", "12"))


def test_invalid_condition_and_blank_category_rejected():
    with pytest.raises(ValueError):
        check_price("Home", "mint", "10", [])
    with pytest.raises(ValueError):
        check_price("   ", "good", "10", [])


def test_zero_price_is_valid_and_low():
    assert check_price("Home", "good", "0", comps("8", "10", "12")).verdict == "low"
