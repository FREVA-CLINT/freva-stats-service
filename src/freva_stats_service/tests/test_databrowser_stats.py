"""Unit tests for the statistics."""

from datetime import datetime
from typing import Any, Dict, List

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
    mongo_databrowser_collection: int,
) -> None:
    """Test adding new query stats."""
    for query in databrowser_search_stats[:mongo_databrowser_collection]:
        json = {"metadata": query["metadata"], "query": query["query"]}
        print(json)
        res = client.post(
            "/api/stats/tests/databrowser/",
            json=json,
        )
        assert res.status_code == 201


@pytest.mark.asyncio
async def test_put_search_method_fail(
    client: TestClient,
    access_token: str,
    databrowser_search_stats: List[Dict[str, Any]],
) -> None:
    """Test the put method."""
    payload = {"metadata": {"foo": "bar"}, "query": {"foo": "bar"}}
    stats = databrowser_search_stats[0].copy()
    res = client.put(
        "/api/stats/docs/databrowser/0/",
        json=payload,
        headers={"access-token": "faketoken"},
    )
    assert res.status_code == 200
    res = client.put(
        "/api/stats/tests/databrowser/0",
        json=payload,
        headers={"access-token": "faketoken"},
    )
    assert res.status_code == 401

    res = client.put(
        "/api/stats/docs/databrowser/0",
        json=payload,
        headers={"access-token": access_token},
    )
    assert res.status_code == 422

    res = client.put(
        "/api/stats/docs/databrowser/0",
        json={"metadata": stats["metadata"], "query": stats["query"]},
        headers={"access-token": access_token},
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_put_search_method_success(
    client: TestClient,
    databrowser_search_stats: List[Dict[str, Any]],
    access_token: str,
    mongo_databrowser_collection: int,
) -> None:
    """Test the put method."""
    payload = {"metadata": {"foo": "bar"}, "query": {"foo": "bar"}}
    stats = databrowser_search_stats[0].copy()
    payload = {"metadata": stats["metadata"], "query": stats["query"]}
    payload["metadata"]["num_results"] = 999
    res = client.put(
        f"/api/stats/docs/databrowser/{stats['_id']}/",
        json=payload,
        headers={"access-token": "faketoken"},
    )
    assert res.status_code == 200
    res = client.post(
        "/api/stats/tests/databrowser",
        json={"metadata": stats["metadata"], "query": stats["query"]},
        headers={"access-token": access_token},
    )
    key = res.json()["id"]

    res = client.put(
        f"/api/stats/tests/databrowser/{key}",
        json={"metadata": stats["metadata"], "query": stats["query"]},
        headers={"access-token": access_token},
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_get_search_method_unauthorised(client: TestClient) -> None:
    """Test the get statistics method."""
    res = client.get("/api/stats/tests/databrowser")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_search_method_authorised(
    client: TestClient, access_token: str, mongo_databrowser_collection: int
) -> None:
    """Test the get statistics method."""
    res = client.get(
        "/api/stats/tests/databrowser",
    )
    assert res.status_code == 401
    res = client.get(
        "/api/stats/tests/databrowser",
        headers={"access-token": access_token},
    )
    assert res.status_code == 200
    assert len(list(res.iter_lines())) == mongo_databrowser_collection + 1
    res = client.get(
        "/api/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"num_results": 0, "before": "2020-02-02"},
    )
    assert res.status_code == 404
    res = client.get(
        "/api/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"server_status": 500},
    )
    assert res.status_code == 404
    res = client.get(
        "/api/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"num_results": 0, "after": "foo"},
    )
    assert res.status_code == 200
    assert len(list(res.iter_lines())) == mongo_databrowser_collection + 1
    res = client.get(
        "/api/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"project": "cmip"},
    )
    assert res.status_code == 200
