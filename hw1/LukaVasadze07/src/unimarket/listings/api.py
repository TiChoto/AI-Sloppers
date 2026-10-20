"""Listings HTTP API.

Member 1 owns this module. It adapts the shared in-memory store to the
contract in ``docs/api.md``. It does not import or call the listing assistant
or the search assistant.
"""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response

from unimarket.listings.model import Listing, ListingCreate, ListingUpdate, parse_price
from unimarket.listings.store import InMemoryListingStore, ListingQuery


def create_listings_router(store: InMemoryListingStore) -> APIRouter:
    """Build the listings routes bound to ``store``."""
    router = APIRouter(tags=["listings"])

    @router.post("/listings", response_model=Listing, status_code=201)
    def create_listing(body: ListingCreate) -> Listing:
        """Create a listing. The system assigns ``id`` and ``created_at``."""
        return store.create(body)

    @router.get("/listings/{id}", response_model=Listing)
    def get_listing(id: str) -> Listing:
        """Return one listing, or 404 when the id is unknown."""
        listing = store.get(id)
        if listing is None:
            raise HTTPException(status_code=404, detail="Listing not found")
        return listing

    @router.patch("/listings/{id}", response_model=Listing)
    def update_listing(id: str, body: ListingUpdate) -> Listing:
        """Update fields the client sent. Invalid fields are 422; unknown id is 404."""
        updated = store.update(id, body)
        if updated is None:
            raise HTTPException(status_code=404, detail="Listing not found")
        return updated

    @router.delete("/listings/{id}", status_code=204)
    def delete_listing(id: str) -> Response:
        """Delete a listing. Unknown ids are 404. The response has no body."""
        if not store.delete(id):
            raise HTTPException(status_code=404, detail="Listing not found")
        return Response(status_code=204)

    @router.get("/listings", response_model=list[Listing])
    def search_listings(
        q: Annotated[
            str | None,
            Query(description="Case-insensitive substring of title or description."),
        ] = None,
        category: Annotated[
            str | None,
            Query(description="Case-insensitive exact category match."),
        ] = None,
        min_price: Annotated[
            str | None,
            Query(description="Inclusive minimum price. Non-negative, at most 2 decimal places."),
        ] = None,
        max_price: Annotated[
            str | None,
            Query(description="Inclusive maximum price. Non-negative, at most 2 decimal places."),
        ] = None,
    ) -> list[Listing]:
        """Return listings that match the structured filters. Newest first."""
        lower = _bound(min_price, "min_price")
        upper = _bound(max_price, "max_price")
        if lower is not None and upper is not None and lower > upper:
            raise HTTPException(status_code=422, detail="min_price must not exceed max_price")
        return store.search(
            ListingQuery(text=q, category=category, min_price=lower, max_price=upper)
        )

    return router


def _bound(value: str | None, field_name: str) -> Decimal | None:
    if value is None:
        return None
    try:
        return parse_price(value, field_name=field_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
