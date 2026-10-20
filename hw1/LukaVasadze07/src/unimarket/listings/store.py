"""In-memory listing store.

Records live in this process only. Restarting the process drops them.
Search applies structured filters (text, category, and price range). It is
not natural-language search and it does not call the search assistant.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from threading import Lock
from uuid import uuid4

from unimarket.listings.model import Listing, ListingCreate, ListingUpdate


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ListingQuery:
    """Structured filters for ``GET /listings``.

    Blank text and blank category are treated as "no filter". Price bounds
    are inclusive. ``None`` leaves that side of the range open.
    """

    text: str | None = None
    category: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None


@dataclass
class _Row:
    listing: Listing
    inserted: int


class InMemoryListingStore:
    """Process-local collection of listings, guarded by a lock.

    ``clock`` defaults to the current UTC time. Tests can pass a clock to
    make ``created_at`` deterministic. The HTTP API does not expose ``clock``.
    """

    def __init__(self, *, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or _utcnow
        self._rows: dict[str, _Row] = {}
        self._next_insert = 0
        self._lock = Lock()

    def create(self, data: ListingCreate) -> Listing:
        """Assign ``id`` and ``created_at``, store the listing, and return it."""
        created_at = self._clock()
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        else:
            created_at = created_at.astimezone(timezone.utc)
        listing = Listing(
            id=str(uuid4()),
            title=data.title,
            description=data.description,
            category=data.category,
            price=data.price,
            condition=data.condition,
            image_ref=data.image_ref,
            created_at=created_at,
        )
        with self._lock:
            self._rows[listing.id] = _Row(listing=listing, inserted=self._next_insert)
            self._next_insert += 1
        return listing

    def get(self, listing_id: str) -> Listing | None:
        """Return the listing, or ``None`` when the id is unknown."""
        with self._lock:
            row = self._rows.get(listing_id)
            return None if row is None else row.listing

    def update(self, listing_id: str, data: ListingUpdate) -> Listing | None:
        """Apply fields the client set. Return ``None`` when the id is unknown."""
        changes = data.model_dump(exclude_unset=True)
        with self._lock:
            row = self._rows.get(listing_id)
            if row is None:
                return None
            updated = row.listing.model_copy(update=changes)
            self._rows[listing_id] = _Row(listing=updated, inserted=row.inserted)
            return updated

    def delete(self, listing_id: str) -> bool:
        """Delete the listing. Return ``False`` when the id is unknown."""
        with self._lock:
            if listing_id not in self._rows:
                return False
            del self._rows[listing_id]
            return True

    def search(self, query: ListingQuery) -> list[Listing]:
        """Return matches, newest ``created_at`` first.

        Listings that share a timestamp are ordered by reverse creation
        order: the one inserted later comes first. Filters combine with AND.

        ``text`` is a case-insensitive substring of the title or the
        description. It does not look at category or condition. ``category``
        is a case-insensitive exact match. Price bounds are inclusive.
        """
        text = "" if query.text is None else query.text.strip().casefold()
        category = "" if query.category is None else query.category.strip().casefold()
        with self._lock:
            snapshot = list(self._rows.values())
        matched: list[_Row] = []
        for row in snapshot:
            listing = row.listing
            if text and text not in listing.title.casefold() and text not in listing.description.casefold():
                continue
            if category and listing.category.casefold() != category:
                continue
            if query.min_price is not None and listing.price < query.min_price:
                continue
            if query.max_price is not None and listing.price > query.max_price:
                continue
            matched.append(row)
        matched.sort(key=lambda row: (row.listing.created_at, row.inserted), reverse=True)
        return [row.listing for row in matched]
