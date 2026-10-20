"""Interface for the AI Listing Assistant.

Member 2 owns this module. The foundation stops at the contract below.
There is no assistant implementation, no model client, and no HTTP route.

The dataclasses are the input and output shape of ``ListingAssistant``.
They are not a stored listing and they are not validated here. An
implementation should follow the constraints in the docstrings and in
``docs/ai-listing-assistant.md``.

This module may depend on ``unimarket.listings.model`` for the shared
``Condition`` enum. It must not import FastAPI, the listings HTTP API, the
listing store, the app factory, or the search assistant.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from unimarket.listings.model import Condition


@dataclass(frozen=True)
class ListingDraft:
    """Rough student input for one listing suggestion.

    ``text`` is the student's draft. Implementations should require non-empty
    text. ``image_ref`` is an optional string reference to an image the
    student already has. It is not an upload and not image bytes. ``None``
    means no image was provided.
    """

    text: str
    image_ref: str | None = None


@dataclass(frozen=True)
class PriceRange:
    """Suggested low and high price, inclusive, in the same units as ``Listing.price``.

    ``minimum`` and ``maximum`` are ``Decimal`` values. Implementations should
    keep both non-negative, use at most two fractional digits, and keep
    ``minimum`` less than or equal to ``maximum``. This range is advice.
    It is not written to the listing store by this interface.
    """

    minimum: Decimal
    maximum: Decimal


@dataclass(frozen=True)
class ListingSuggestion:
    """Fields the assistant proposes. The student still creates the listing.

    ``title``, ``description``, and ``category`` are non-empty text.
    ``condition`` is one of the shared ``Condition`` values. ``price_range``
    is a suggestion, not the listing's ``price``.
    """

    title: str
    description: str
    category: str
    condition: Condition
    price_range: PriceRange


class ListingAssistant(Protocol):
    """Suggest listing fields from a rough student draft.

    ``suggest`` does not create, update, or delete a listing. The caller
    shows the suggestion to the student. A listing exists only after the
    listings API accepts ``POST /listings``.

    Implementations own any model call. None is provided here.
    """

    def suggest(self, draft: ListingDraft) -> ListingSuggestion:
        """Return a title, description, category, condition, and price range.

        ``draft.text`` is the rough description. ``draft.image_ref``, when
        set, is a string reference the implementation may use. This protocol
        does not define how, or whether, an implementation reads image bytes.
        """
        ...
