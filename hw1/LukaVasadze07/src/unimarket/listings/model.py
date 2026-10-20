"""Shared listing data model.

A listing is one second-hand item offered by a student. Clients send the
item fields. The system assigns ``id`` and ``created_at``.

``condition`` is the closed enum documented on ``Condition``. ``category`` is
required free text; this foundation does not define a fixed category list.
``image_ref`` is an optional string reference, not an upload and not image bytes.
``price`` is a non-negative decimal with at most two fractional digits.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    field_serializer,
    field_validator,
    model_validator,
)


class Condition(str, Enum):
    """Physical condition of a second-hand item.

    Values are lowercase and matched exactly:

    - ``new``: unused; tags or original packaging may still be attached
    - ``like_new``: barely used, with no visible wear
    - ``good``: used, with light wear, and fully functional
    - ``fair``: used, with noticeable wear, and still usable
    - ``poor``: heavily used or damaged; may need repair
    """

    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


def require_text(value: object) -> str:
    """Return stripped text, or raise ``ValueError`` when it is empty."""
    if not isinstance(value, str):
        raise ValueError("must be non-empty text")
    text = value.strip()
    if not text:
        raise ValueError("must be non-empty text")
    return text


def optional_image_ref(value: object) -> str | None:
    """Return a stripped image reference, or ``None`` when the value is null."""
    if value is None:
        return None
    return require_text(value)


def parse_price(value: object, *, field_name: str = "price") -> Decimal:
    """Parse a non-negative price with at most two fractional digits.

    Integers, finite floats, numeric strings, and ``Decimal`` values are
    accepted. Booleans, blank text, negative numbers, non-finite numbers,
    and values that are not exactly representable in cents are rejected.
    The returned ``Decimal`` has cent scale, for example ``Decimal('8.00')``.
    """
    invalid = f"{field_name} must be a non-negative number with at most 2 decimal places"
    if isinstance(value, bool) or value is None:
        raise ValueError(invalid)
    if isinstance(value, Decimal):
        amount = value
    elif isinstance(value, int):
        amount = Decimal(value)
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(invalid)
        amount = Decimal(str(value))
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError(invalid)
        try:
            amount = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(invalid) from exc
    else:
        raise ValueError(invalid)
    if not amount.is_finite() or amount < 0:
        raise ValueError(invalid)
    cents = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if cents != amount:
        raise ValueError(f"{field_name} must have at most 2 decimal places")
    return cents


RequiredText = Annotated[str, BeforeValidator(require_text)]
OptionalImageRef = Annotated[str | None, BeforeValidator(optional_image_ref)]
PriceInput = Annotated[Decimal, BeforeValidator(parse_price)]


class ListingCreate(BaseModel):
    """Fields a client may send to create a listing.

    ``id`` and ``created_at`` are rejected. Surrounding whitespace on text
    fields and ``image_ref`` is removed before the listing is stored.
    """

    model_config = ConfigDict(extra="forbid")

    title: RequiredText
    description: RequiredText
    category: RequiredText
    price: PriceInput
    condition: Condition
    image_ref: OptionalImageRef = None


class ListingUpdate(BaseModel):
    """Partial update. Omitted fields stay as they are.

    Unknown fields, including ``id`` and ``created_at``, are rejected.
    Explicit null is rejected for title, description, category, price, and
    condition. Explicit null for ``image_ref`` clears the reference.
    """

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    category: str | None = None
    price: Decimal | None = None
    condition: Condition | None = None
    image_ref: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_required_fields(cls, data: object) -> object:
        if isinstance(data, dict):
            for name in ("title", "description", "category", "price", "condition"):
                if name in data and data[name] is None:
                    raise ValueError(f"{name} must not be null")
        return data

    @field_validator("title", "description", "category")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return require_text(value)

    @field_validator("price", mode="before")
    @classmethod
    def check_price(cls, value: object) -> Decimal | None:
        if value is None:
            return None
        return parse_price(value)

    @field_validator("image_ref", mode="before")
    @classmethod
    def check_image_ref(cls, value: object) -> str | None:
        return optional_image_ref(value)


class Listing(BaseModel):
    """One stored listing, including the system-assigned identity fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    title: str
    description: str
    category: str
    price: Decimal
    condition: Condition
    image_ref: str | None = None
    created_at: datetime

    @field_serializer("price")
    def serialize_price(self, value: Decimal) -> str:
        return f"{value:.2f}"

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        return value.isoformat().replace("+00:00", "Z")
