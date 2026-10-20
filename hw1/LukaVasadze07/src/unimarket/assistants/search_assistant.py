"""Interface for smart search and the RAG assistant.

Member 3 owns this module. The foundation stops at the contract below.
There is no index, no embedding model, no vector database, and no HTTP route.

Structured filters stay on ``GET /listings`` (see ``unimarket.listings``).
This protocol is the separate natural-language path: index a listing, remove
it, and answer a question with ranked listing ids plus a short reason.

This module may depend on ``unimarket.listings.model`` for the stored
``Listing`` shape. It must not import FastAPI, the listings HTTP API, the
listing store, the app factory, or the listing assistant. The listings API
does not call this protocol.
"""

from dataclasses import dataclass
from typing import Protocol, Sequence

from unimarket.listings.model import Listing


@dataclass(frozen=True)
class RankedListing:
    """One natural-language search hit.

    ``listing_id`` is ``Listing.id``. ``reason`` is a short explanation a
    student can read. Rank is the position in the sequence returned by
    ``SearchAssistant.query``: index 0 is the best match. This contract has
    no separate score field.
    """

    listing_id: str
    reason: str


class SearchAssistant(Protocol):
    """Index listings and answer natural-language queries.

    The listings API does not call these methods. A later integration has to
    be added deliberately in shared code; it is not part of this foundation.

    Implementations choose how to index and rank. Embeddings and a vector
    database are not required by this protocol.
    """

    def index_listing(self, listing: Listing) -> None:
        """Add ``listing`` to the index, or replace the entry with the same id.

        The listing is whatever the caller passes. This method does not read
        the listing store and does not check that the id still exists there.
        """
        ...

    def remove_listing(self, listing_id: str) -> None:
        """Remove ``listing_id`` from the index.

        Removing an id that is not indexed is a no-op. After removal, later
        ``query`` results must not include that id until it is indexed again.
        """
        ...

    def query(self, text: str) -> Sequence[RankedListing]:
        """Answer a natural-language query with ranked listing ids.

        ``text`` is a question or phrase, not the ``q`` / ``category`` /
        ``min_price`` / ``max_price`` filters of ``GET /listings``.

        Return the best match first. Include only indexed listings, with no
        duplicate ids. Each item carries a short human-readable reason.
        An empty sequence means nothing matched. Blank or whitespace-only
        ``text`` returns an empty sequence.

        This method does not create embeddings and does not open a vector
        database; an implementation may, behind this signature.
        """
        ...
