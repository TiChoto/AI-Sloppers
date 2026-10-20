"""Shared FastAPI application factory.

``create_app`` wires the listings router to an in-memory store. It does not
construct or call the listing assistant or the search assistant. Uvicorn
loads the module-level ``app`` object.
"""

from fastapi import FastAPI

from unimarket.listings.api import create_listings_router
from unimarket.listings.store import InMemoryListingStore


def create_app(store: InMemoryListingStore | None = None) -> FastAPI:
    """Return the UniMarket API.

    Pass ``store`` when a caller needs an isolated collection, such as a test.
    When ``store`` is omitted, the app keeps a new in-memory store for the
    life of the process.
    """
    listing_store = InMemoryListingStore() if store is None else store
    app = FastAPI(
        title="UniMarket",
        version="0.1.0",
        description=(
            "Shared foundation for a student second-hand marketplace. "
            "This service stores listings in memory and exposes the listings HTTP contract. "
            "It does not call the listing assistant or the search assistant."
        ),
    )
    app.state.listing_store = listing_store
    app.include_router(create_listings_router(listing_store))
    return app


app = create_app()
