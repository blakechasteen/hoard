"""Integration tests for portfolio summary."""

import pytest


@pytest.mark.asyncio
async def test_empty_portfolio(client, auth_headers):
    resp = await client.get("/api/v1/portfolio/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["item_count"] == 0
    assert data["total_value"] is None


@pytest.mark.asyncio
async def test_portfolio_with_items(client, auth_headers):
    # Create items with purchase prices
    item1 = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Charizard", "category": "pokemon", "purchase_price": 100.0,
    })
    item2 = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Blastoise", "category": "pokemon", "purchase_price": 50.0,
    })

    # Add appraisals
    await client.post(
        f"/api/v1/items/{item1.json()['id']}/appraisals",
        headers=auth_headers, json={"price": 200.0, "confidence": 0.9},
    )
    await client.post(
        f"/api/v1/items/{item2.json()['id']}/appraisals",
        headers=auth_headers, json={"price": 80.0, "confidence": 0.7},
    )

    resp = await client.get("/api/v1/portfolio/summary", headers=auth_headers)
    data = resp.json()
    assert data["item_count"] == 2
    assert data["total_value"] == 280.0
    assert data["total_cost"] == 150.0
    assert data["total_gain"] == pytest.approx(130.0)
    assert data["gain_pct"] == pytest.approx(86.67, rel=0.01)


@pytest.mark.asyncio
async def test_portfolio_with_pinned_value(client, auth_headers):
    item = await client.post("/api/v1/items", headers=auth_headers, json={
        "name": "Rare Coin", "category": "coins", "purchase_price": 500.0,
    })
    item_id = item.json()["id"]

    # Pin a value instead of appraisal
    await client.patch(f"/api/v1/items/{item_id}", headers=auth_headers, json={
        "pinned_value": 750.0,
    })

    resp = await client.get("/api/v1/portfolio/summary", headers=auth_headers)
    data = resp.json()
    assert data["total_value"] == 750.0
    assert data["high_confidence_count"] == 1  # pinned values are high confidence
