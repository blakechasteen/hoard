"""Integration tests for items CRUD."""

import pytest


@pytest.mark.asyncio
async def test_create_item(client, auth_headers):
    resp = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Charizard Base Set Holo",
        "category": "pokemon",
        "grade": "PSA 9",
        "purchase_price": 350.0,
        "tags": ["base set", "holo", "1st gen"],
        "metadata": {"set_number": "4/102", "edition": "unlimited"},
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Charizard Base Set Holo"
    assert data["category"] == "pokemon"
    assert data["grade"] == "PSA 9"
    assert data["purchase_price"] == 350.0
    assert "base set" in data["tags"]
    assert data["metadata"]["set_number"] == "4/102"
    assert data["current_value"] is None  # no appraisals yet


@pytest.mark.asyncio
async def test_list_items(client, auth_headers):
    # Create two items
    await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Pikachu Illustrator", "category": "pokemon",
    })
    await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "1909 T206 Honus Wagner", "category": "sports",
    })

    resp = await client.get("/api/v1/items", headers=auth_headers)
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2


@pytest.mark.asyncio
async def test_list_items_filter_category(client, auth_headers):
    await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Pikachu", "category": "pokemon",
    })
    await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Morgan Dollar", "category": "coins",
    })

    resp = await client.get("/api/v1/items?category=pokemon", headers=auth_headers)
    items = resp.json()
    assert len(items) == 1
    assert items[0]["category"] == "pokemon"


@pytest.mark.asyncio
async def test_update_item(client, auth_headers):
    create_resp = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Charizard", "category": "pokemon", "grade": "raw",
    })
    item_id = create_resp.json()["id"]

    resp = await client.patch(f"/api/v1/items/{item_id}", headers=auth_headers, json={
        "grade": "PSA 10",
        "pinned_value": 5000.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["grade"] == "PSA 10"
    assert data["pinned_value"] == 5000.0
    assert data["current_value"] == 5000.0  # pinned value becomes current
    assert data["current_confidence"] == 1.0


@pytest.mark.asyncio
async def test_delete_item(client, auth_headers):
    create_resp = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Junk Card", "category": "pokemon",
    })
    item_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_item_not_found(client, auth_headers):
    resp = await client.get("/api/v1/items/nonexistent-id", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_invalid_category(client, auth_headers):
    resp = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Something", "category": "invalid_category",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_item_with_appraisal_shows_value(client, auth_headers):
    create_resp = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Blastoise", "category": "pokemon", "purchase_price": 50.0,
    })
    item_id = create_resp.json()["id"]

    await client.post(f"/api/v1/items/{item_id}/appraisals", headers=auth_headers, json={
        "price": 120.0,
        "source": "manual",
        "confidence": 0.8,
    })

    resp = await client.get(f"/api/v1/items/{item_id}", headers=auth_headers)
    data = resp.json()
    assert data["current_value"] == 120.0
    assert data["value_change_pct"] == pytest.approx(140.0)  # (120-50)/50 * 100
