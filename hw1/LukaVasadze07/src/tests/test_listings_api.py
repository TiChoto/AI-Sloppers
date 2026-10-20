"""Contract tests for the listings HTTP API."""

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from unimarket.app import create_app
from unimarket.assistants.listing_assistant import ListingAssistant
from unimarket.assistants.search_assistant import SearchAssistant
from unimarket.listings.store import InMemoryListingStore

ROOT = Path(__file__).resolve().parents[1]


def payload(**overrides: object) -> dict[str, object]:
    body: dict[str, object] = {
        "title": "Desk lamp",
        "description": "Warm light, works well",
        "category": "Home",
        "price": "12.50",
        "condition": "good",
        "image_ref": "photos/lamp",
    }
    body.update(overrides)
    return body


@pytest.fixture
def client() -> TestClient:
    app = create_app(InMemoryListingStore())
    with TestClient(app) as test_client:
        yield test_client


def test_list_is_empty_before_any_create(client: TestClient) -> None:
    response = client.get("/listings")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_retrieve(client: TestClient) -> None:
    created = client.post("/listings", json=payload(price=12.5))
    assert created.status_code == 201, created.text
    body = created.json()
    assert set(body) == {
        "id",
        "title",
        "description",
        "category",
        "price",
        "condition",
        "image_ref",
        "created_at",
    }
    assert body["title"] == "Desk lamp"
    assert body["price"] == "12.50"
    assert body["condition"] == "good"
    assert body["image_ref"] == "photos/lamp"
    assert body["created_at"].endswith("Z")
    fetched = client.get(f"/listings/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_retrieve_missing_is_404(client: TestClient) -> None:
    response = client.get("/listings/missing")
    assert response.status_code == 404
    assert response.json() == {"detail": "Listing not found"}


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": " "},
        {"price": -1},
        {"price": "1.234"},
        {"condition": "broken"},
        {"id": "client-chosen"},
        {"created_at": "2026-10-20T00:00:00Z"},
    ],
)
def test_create_rejects_invalid_payload(client: TestClient, overrides: dict[str, object]) -> None:
    response = client.post("/listings", json=payload(**overrides))
    assert response.status_code == 422
    assert client.get("/listings").json() == []


def test_patch_updates_only_provided_fields(client: TestClient) -> None:
    original = client.post("/listings", json=payload()).json()
    patched = client.patch(
        f"/listings/{original['id']}",
        json={"title": "Reading lamp", "image_ref": None},
    )
    assert patched.status_code == 200, patched.text
    body = patched.json()
    assert body["title"] == "Reading lamp"
    assert body["image_ref"] is None
    assert body["description"] == original["description"]
    assert body["category"] == original["category"]
    assert body["price"] == original["price"]
    assert body["condition"] == original["condition"]
    assert body["id"] == original["id"]
    assert body["created_at"] == original["created_at"]

    same = client.patch(f"/listings/{original['id']}", json={})
    assert same.status_code == 200
    assert same.json() == body


def test_patch_missing_is_404(client: TestClient) -> None:
    response = client.patch("/listings/missing", json={"title": "Anything"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Listing not found"}


def test_patch_invalid_body_on_missing_id_is_422(client: TestClient) -> None:
    response = client.patch("/listings/missing", json={"price": -1})
    assert response.status_code == 422


def test_patch_invalid_does_not_change_listing(client: TestClient) -> None:
    original = client.post("/listings", json=payload()).json()
    response = client.patch(
        f"/listings/{original['id']}",
        json={"condition": "mint", "title": "Should not stick"},
    )
    assert response.status_code == 422
    assert client.get(f"/listings/{original['id']}").json() == original


def test_delete(client: TestClient) -> None:
    listing_id = client.post("/listings", json=payload()).json()["id"]
    deleted = client.delete(f"/listings/{listing_id}")
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/listings/{listing_id}").status_code == 404
    assert client.get("/listings").json() == []


def test_delete_missing_is_404(client: TestClient) -> None:
    response = client.delete("/listings/missing")
    assert response.status_code == 404
    assert response.json() == {"detail": "Listing not found"}


def test_search_filters(client: TestClient) -> None:
    textbook = client.post(
        "/listings",
        json=payload(
            title="Calculus textbook",
            description="No highlights",
            category="Textbooks",
            price="20.00",
            condition="good",
            image_ref=None,
        ),
    ).json()
    lamp = client.post(
        "/listings",
        json=payload(
            title="Lamp",
            description="For late calculus problem sets",
            category="Home",
            price="8.00",
            condition="fair",
        ),
    ).json()
    bike = client.post(
        "/listings",
        json=payload(
            title="Bike",
            description="City bike",
            category="Transport",
            price="60.00",
            condition="good",
        ),
    ).json()

    def ids(response):
        assert response.status_code == 200, response.text
        return {item["id"] for item in response.json()}

    assert ids(client.get("/listings")) == {textbook["id"], lamp["id"], bike["id"]}
    assert ids(client.get("/listings", params={"q": "calculus"})) == {textbook["id"], lamp["id"]}
    assert ids(client.get("/listings", params={"q": "transport"})) == set()
    assert ids(client.get("/listings", params={"q": "   "})) == {
        textbook["id"],
        lamp["id"],
        bike["id"],
    }
    assert ids(client.get("/listings", params={"category": " HOME "})) == {lamp["id"]}
    assert ids(client.get("/listings", params={"min_price": "20"})) == {
        textbook["id"],
        bike["id"],
    }
    assert ids(client.get("/listings", params={"max_price": "20"})) == {
        textbook["id"],
        lamp["id"],
    }
    assert ids(
        client.get("/listings", params={"q": "calculus", "category": "Textbooks"})
    ) == {textbook["id"]}


def test_search_price_range_is_inclusive(client: TestClient) -> None:
    free = client.post("/listings", json=payload(title="Box", price="0.00")).json()
    ten = client.post("/listings", json=payload(title="Mug", price="10.00")).json()
    just_over = client.post("/listings", json=payload(title="Plate", price="10.01")).json()

    exact = client.get("/listings", params={"min_price": "10", "max_price": "10.00"})
    assert exact.status_code == 200
    assert [item["id"] for item in exact.json()] == [ten["id"]]

    zero = client.get("/listings", params={"min_price": "0", "max_price": "0"})
    assert [item["id"] for item in zero.json()] == [free["id"]]

    opened = client.get("/listings", params={"min_price": "10"})
    assert {item["id"] for item in opened.json()} == {ten["id"], just_over["id"]}


@pytest.mark.parametrize(
    "params",
    [
        {"min_price": "-0.01"},
        {"max_price": "abc"},
        {"min_price": "10.001"},
        {"min_price": "30", "max_price": "10"},
    ],
)
def test_search_rejects_invalid_price_query(client: TestClient, params: dict[str, str]) -> None:
    response = client.get("/listings", params=params)
    assert response.status_code == 422


def test_search_inverted_range_names_the_problem(client: TestClient) -> None:
    response = client.get("/listings", params={"min_price": "30", "max_price": "10"})
    assert response.status_code == 422
    assert response.json()["detail"] == "min_price must not exceed max_price"


def test_list_is_newest_first() -> None:
    moments = [
        datetime(2026, 10, 20, 12, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc),
        datetime(2026, 10, 20, 13, 0, tzinfo=timezone.utc),
    ]
    cursor = {"index": 0}

    def clock() -> datetime:
        current = moments[cursor["index"]]
        cursor["index"] += 1
        return current

    with TestClient(create_app(InMemoryListingStore(clock=clock))) as client:
        created = [
            client.post("/listings", json=payload(title=title)).json()["id"]
            for title in ("first", "second", "third")
        ]
        listed = [item["id"] for item in client.get("/listings").json()]
        assert listed == [created[2], created[1], created[0]]


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_listings_api_does_not_import_assistants() -> None:
    modules = _imported_modules(ROOT / "unimarket/listings/api.py")
    assert all("assistants" not in name for name in modules)
    app_modules = _imported_modules(ROOT / "unimarket/app.py")
    assert all("assistants" not in name for name in app_modules)
    package_modules = _imported_modules(ROOT / "unimarket/listings/__init__.py")
    assert package_modules == {
        "unimarket.listings.model",
        "unimarket.listings.store",
    }


def test_assistant_modules_do_not_import_fastapi() -> None:
    forbidden = {
        "fastapi",
        "unimarket.app",
        "unimarket.listings.api",
        "unimarket.listings.store",
    }
    for relative in (
        "unimarket/assistants/__init__.py",
        "unimarket/assistants/listing_assistant.py",
        "unimarket/assistants/search_assistant.py",
    ):
        modules = _imported_modules(ROOT / relative)
        assert modules.isdisjoint(forbidden)
        assert all(not name.startswith("fastapi.") for name in modules)
    assert hasattr(ListingAssistant, "suggest")
    assert hasattr(SearchAssistant, "index_listing")
    assert hasattr(SearchAssistant, "remove_listing")
    assert hasattr(SearchAssistant, "query")
