"""Contract tests for the shared listing model."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from unimarket.listings.model import Condition, Listing, ListingCreate, ListingUpdate


def _create(**overrides: object) -> ListingCreate:
    payload: dict[str, object] = {
        "title": "  Desk lamp  ",
        "description": " Warm light ",
        "category": " Home ",
        "price": "12.50",
        "condition": "good",
    }
    payload.update(overrides)
    return ListingCreate.model_validate(payload)


def test_create_strips_text_and_accepts_decimal_string() -> None:
    listing = _create(image_ref="  photos/lamp  ")
    assert listing.title == "Desk lamp"
    assert listing.description == "Warm light"
    assert listing.category == "Home"
    assert listing.price == Decimal("12.50")
    assert listing.condition is Condition.GOOD
    assert listing.image_ref == "photos/lamp"
    assert "id" not in ListingCreate.model_fields
    assert "created_at" not in ListingCreate.model_fields


@pytest.mark.parametrize("price", [0, "0", "0.00", 8, "8.50", Decimal("19.99")])
def test_create_accepts_non_negative_cent_prices(price: object) -> None:
    listing = _create(price=price)
    assert listing.price >= 0
    assert listing.price == listing.price.quantize(Decimal("0.01"))


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": " "},
        {"description": ""},
        {"category": "   "},
        {"title": None},
        {"price": -1},
        {"price": "-0.01"},
        {"price": "0.001"},
        {"price": True},
        {"price": "free"},
        {"condition": "Good"},
        {"condition": "broken"},
        {"image_ref": "  "},
        {"id": "client-chosen"},
        {"created_at": "2026-10-20T00:00:00Z"},
    ],
)
def test_create_rejects_invalid_fields(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        _create(**overrides)


def test_create_allows_missing_image_ref() -> None:
    assert _create().image_ref is None
    assert _create(image_ref=None).image_ref is None


def test_condition_values() -> None:
    assert [item.value for item in Condition] == [
        "new",
        "like_new",
        "good",
        "fair",
        "poor",
    ]


def test_update_changes_only_fields_that_were_sent() -> None:
    untouched = ListingUpdate.model_validate({})
    assert untouched.model_dump(exclude_unset=True) == {}

    renamed = ListingUpdate.model_validate({"title": "  Lamp  ", "price": 3.5})
    assert renamed.model_dump(exclude_unset=True) == {
        "title": "Lamp",
        "price": Decimal("3.50"),
    }

    cleared = ListingUpdate.model_validate({"image_ref": None})
    assert cleared.model_fields_set == {"image_ref"}
    assert cleared.image_ref is None


@pytest.mark.parametrize(
    "payload",
    [
        {"title": None},
        {"description": None},
        {"category": None},
        {"price": None},
        {"condition": None},
        {"title": " "},
        {"price": -1},
        {"price": "1.234"},
        {"condition": "broken"},
        {"image_ref": ""},
        {"id": "client-chosen"},
        {"created_at": "2026-10-20T00:00:00Z"},
    ],
)
def test_update_rejects_invalid_fields(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ListingUpdate.model_validate(payload)


def test_listing_json_uses_cent_string_and_utc_timestamp() -> None:
    listing = Listing(
        id="2c0f1a3e-7b4d-4e1a-9c2f-0a1b2c3d4e5f",
        title="Desk lamp",
        description="Warm light",
        category="Home",
        price=Decimal("12.5"),
        condition=Condition.GOOD,
        image_ref=None,
        created_at=datetime(2026, 10, 20, 16, 35, 1, 123456, tzinfo=timezone.utc),
    )
    dumped = listing.model_dump(mode="json")
    assert dumped == {
        "id": "2c0f1a3e-7b4d-4e1a-9c2f-0a1b2c3d4e5f",
        "title": "Desk lamp",
        "description": "Warm light",
        "category": "Home",
        "price": "12.50",
        "condition": "good",
        "image_ref": None,
        "created_at": "2026-10-20T16:35:01.123456Z",
    }
