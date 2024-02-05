"""Test for the oauth2 token."""

import os
import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_create_token_failed(client: TestClient) -> None:
    """Test failiour of the creation of the access token."""

    res = client.post("/api/token", data={"password": "foo"})
    assert res.status_code == 422
    res = client.post(
        "/api/token", data={"password": "foo", "username": "bar"}
    )
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_create_token_success(client: TestClient) -> None:
    """Test the sucessfull token cration."""

    res = client.post(
        "/api/token",
        data={
            "password": os.environ["API_PASSWORD"],
            "username": os.environ["API_USERNAME"],
        },
        params={"expires_in": ["a", -1, 2]},
    )
    assert res.status_code == 201
    res_json = res.json()
    assert "access_token" in res_json

    res = client.post(
        "/api/token",
        data={
            "password": os.environ["API_PASSWORD"],
            "username": os.environ["API_USERNAME"],
        },
    )
    assert res.status_code == 201
    res_json = res.json()
    assert "access_token" in res_json
