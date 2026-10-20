"""Deterministic local search implementation for UniMarket's search contract.

The assistant stores a snapshot of each indexed listing and ranks query terms
by their strongest matching field. It uses no model, network, or persistence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from threading import RLock
from typing import Protocol

TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
FIELD_WEIGHTS = (("title", 4), ("category", 3), ("condition", 2), ("description", 1))
STOP_WORDS = frozenset({
    "a", "an", "the", "for", "to", "in", "on", "of", "and", "or", "i",
    "me", "my", "with", "please", "looking", "find", "want", "need",
})


class ListingLike(Protocol):
    """The subset of the shared Listing model used by this assistant."""

    id: str
    title: str
    description: str
    category: str
    condition: object


@dataclass(frozen=True)
class RankedListing:
    """One result, compatible with the team SearchAssistant contract."""

    listing_id: str
    reason: str


@dataclass(frozen=True)
class _IndexedListing:
    listing_id: str
    title: str
    description: str
    category: str
    condition: str


def _tokens(value: str) -> tuple[str, ...]:
    """Return unique Unicode word tokens in first-seen order."""
    return tuple(dict.fromkeys(token.casefold() for token in TOKEN.findall(value)))


def _condition_text(value: object) -> str:
    """Handle the shared model's string Enum as well as plain strings."""
    enum_value = getattr(value, "value", value)
    return enum_value if isinstance(enum_value, str) else str(enum_value)


class LocalKeywordSearch:
    """Rank indexed listings by lexical overlap with a student's query.

    Per query token, only the best matching field contributes to the score:
    title 4, category 3, condition 2, description 1. Ties are stable by
    case-insensitive title and then ID. Re-indexing replaces the prior
    snapshot for an ID; removing an unknown ID is harmless.
    """

    def __init__(self) -> None:
        self._listings: dict[str, _IndexedListing] = {}
        self._lock = RLock()

    def index_listing(self, listing: ListingLike) -> None:
        """Add or replace a listing snapshot using the shared model fields."""
        listing_id = listing.id
        if not isinstance(listing_id, str) or not listing_id.strip():
            raise ValueError("listing id must be non-empty text")
        fields = (listing.title, listing.description, listing.category)
        if any(not isinstance(value, str) for value in fields):
            raise ValueError("listing text fields must be strings")
        snapshot = _IndexedListing(
            listing_id=listing_id,
            title=listing.title,
            description=listing.description,
            category=listing.category,
            condition=_condition_text(listing.condition),
        )
        with self._lock:
            self._listings[listing_id] = snapshot

    def remove_listing(self, listing_id: str) -> None:
        """Remove an indexed ID; an absent ID is a no-op."""
        with self._lock:
            self._listings.pop(listing_id, None)

    def query(self, text: str) -> list[RankedListing]:
        """Return matching IDs in deterministic relevance order.

        This is lexical search: it does not infer synonyms, price intent, or
        facts that are absent from the indexed listing text.
        """
        if not isinstance(text, str):
            raise TypeError("query text must be a string")
        query_terms = tuple(token for token in _tokens(text) if token not in STOP_WORDS)
        if not query_terms:
            return []

        with self._lock:
            listings = tuple(self._listings.values())

        ranked: list[tuple[int, str, str, RankedListing]] = []
        for listing in listings:
            by_field = {
                "title": set(_tokens(listing.title)),
                "category": set(_tokens(listing.category)),
                "condition": set(_tokens(listing.condition)),
                "description": set(_tokens(listing.description)),
            }
            matched: dict[str, list[str]] = {name: [] for name, _ in FIELD_WEIGHTS}
            score = 0
            for term in query_terms:
                for field_name, weight in FIELD_WEIGHTS:
                    if term in by_field[field_name]:
                        matched[field_name].append(term)
                        score += weight
                        break
            if score == 0:
                continue

            reason_parts = [
                f"{field_name} terms: {', '.join(matched[field_name])}"
                for field_name, _ in FIELD_WEIGHTS
                if matched[field_name]
            ]
            reason = "Matched " + "; ".join(reason_parts) + "."
            result = RankedListing(listing.listing_id, reason)
            ranked.append((score, listing.title.casefold(), listing.listing_id, result))

        ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
        return [item[3] for item in ranked]
