"""Integration tests for troves (groupings)."""

import pytest


@pytest.mark.asyncio
async def test_create_trove(client, auth_headers):
    resp = await client.post("/api/v1/troves", headers=auth_headers, json={
        "name": "Graded Pokemon",
        "description": "All PSA graded Pokemon cards",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Graded Pokemon"
    assert data["item_count"] == 0


@pytest.mark.asyncio
async def test_create_trove_with_items(client, auth_headers):
    item1 = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Charizard", "category": "pokemon",
    })
    item2 = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Blastoise", "category": "pokemon",
    })

    resp = await client.post("/api/v1/troves", headers=auth_headers, json={
        "name": "Base Set Starters",
        "item_ids": [item1.json()["id"], item2.json()["id"]],
    })
    assert resp.status_code == 201
    assert resp.json()["item_count"] == 2


@pytest.mark.asyncio
async def test_add_item_to_trove(client, auth_headers):
    trove_resp = await client.post("/api/v1/troves", headers=auth_headers, json={
        "name": "My Trove",
    })
    trove_id = trove_resp.json()["id"]

    item_resp = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Pikachu", "category": "pokemon",
    })
    item_id = item_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/troves/{trove_id}/items/{item_id}", headers=auth_headers
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_remove_item_from_trove(client, auth_headers):
    item_resp = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Pikachu", "category": "pokemon",
    })
    item_id = item_resp.json()["id"]

    trove_resp = await client.post("/api/v1/troves", headers=auth_headers, json={
        "name": "My Trove", "item_ids": [item_id],
    })
    trove_id = trove_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/troves/{trove_id}/items/{item_id}", headers=auth_headers
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_list_troves(client, auth_headers):
    await client.post("/api/v1/troves", headers=auth_headers, json={"name": "Trove A"})
    await client.post("/api/v1/troves", headers=auth_headers, json={"name": "Trove B"})

    resp = await client.get("/api/v1/troves", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
