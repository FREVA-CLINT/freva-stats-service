"""Unit tests for the statistics."""
from datetime import datetime
import os
from typing import List, Dict, Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_post_search_method_wrong_types(
    client: TestClient,
) -> None:
    """Test the schema validation."""
    payload = {"metadata": {"foo": "bar"}, "query": {"foo": "bar"}}
    res = client.post(
        "/api/stats/docs/databrowser/",
        json=payload,
        headers={"access-token": "foo"},
    )
    assert res.status_code == 201
    res = client.post(
        "/api/stats/tests/databrowser/",
        json=payload,
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_post_search_method_authorised(
    client: TestClient,
    databrowser_search_stats: List[Dict[str, Any]],
) -> None:
    """Test adding new query stats."""
    for query in databrowser_search_stats:
        json = {"metadata": query["metadata"], "query": query["query"]}
        res = client.post(
            "/api/stats/tests/databrowser/",
            json=json,
        )
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_put_search_method_fail(
    client: TestClient,
    databrowser_search_stats: List[Dict[str, Any]],
    access_token: str,
) -> None:
    """Test the put method."""
    payload = {"metadata": {"foo": "bar"}, "query": {"foo": "bar"}}
    _id = databrowser_search_stats[0]["_id"]
    res = client.put(
        f"/api/stats/docs/databrowser/{_id}/",
        data=payload,
        headers={"access-token": "faketoken"},
    )
    assert res.status_code == 200
    res = client.put(
        f"/api/stats/tests/databrowser/{_id}",
        data=payload,
        headers={"access-token": "faketoken"},
    )
    assert res.status_code == 401

    res = client.put(
        f"/api/stats/docs/databrowser/{_id}",
        data=payload,
        headers={"access-token": access_token},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_get_search_method_unauthorised(client: TestClient) -> None:
    """Test the get statistics method."""
    res = client.get("/api/stats/tests/databrowser")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_search_method_authorised(
    client: TestClient,
    databrowser_search_stats: List[Dict[str, Any]],
    access_token: str,
) -> None:
    """Test the get statistics method."""
    res = client.get(
        "/api/stats/tests/databrowser",
        headers={"access-token": access_token},
    )
    assert int(res.status_code) not in (401, 404)
    assert len(list(res.iter_lines())) == len(databrowser_search_stats) + 1
