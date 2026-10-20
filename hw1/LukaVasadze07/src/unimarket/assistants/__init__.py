"""Assistant interfaces.

These modules declare Protocols only. They do not call a model, build an
index, or register HTTP routes.
"""

from unimarket.assistants.listing_assistant import (
    ListingAssistant,
    ListingDraft,
    ListingSuggestion,
    PriceRange,
)
from unimarket.assistants.search_assistant import RankedListing, SearchAssistant

__all__ = [
    "ListingAssistant",
    "ListingDraft",
    "ListingSuggestion",
    "PriceRange",
    "RankedListing",
    "SearchAssistant",
]
