"""Integration tests for auth endpoints."""

import pytest


@pytest.mark.asyncio
async def test_register_with_valid_invite(client, invite_code):
    resp = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "display_name": "New User",
        "password": "securepass123",
        "invite_code": invite_code,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_with_bad_invite(client):
    resp = await client.post("/api/v1/auth/register", json={
        "username": "newuser",
        "display_name": "New User",
        "password": "securepass123",
        "invite_code": "bogus-code",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_register_duplicate_username(client, invite_code, test_user, db_session):
    # Create a second invite code for the second registration attempt
    import secrets
    from hoard.models import InviteCode
    code2 = secrets.token_urlsafe(8)
    db_session.add(InviteCode(code=code2))
    await db_session.commit()

    resp = await client.post("/api/v1/auth/register", json={
        "username": "testuser",  # same as test_user
        "display_name": "Another User",
        "password": "securepass123",
        "invite_code": code2,
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    resp = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_bad_password(client, test_user):
    resp = await client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(client, auth_headers):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403)  # no bearer token
