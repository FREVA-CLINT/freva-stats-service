"""Unit tests for the statistics."""

from typing import Any, Dict, List
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_post_search_method_wrong_types(
    client: TestClient,
) -> None:
    """Test the schema validation."""
    payload = {"metadata": {"foo": "bar"}, "query": {"foo": "bar"}}
    res = client.post(
        "/api/storage/stats/tests/databrowser/",
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
    stats = databrowser_search_stats[0]
    json = {"metadata": stats["metadata"], "query": stats["query"]}
    res = client.post(
        "/api/storage/stats/example-project/databrowser/",
        json=json,
    )
    assert res.status_code == 201
    for query in databrowser_search_stats[:mongo_databrowser_collection]:
        json = {"metadata": query["metadata"], "query": query["query"]}
        res = client.post(
            "/api/storage/stats/tests/databrowser/",
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
        "/api/storage/stats/example-project/databrowser/0/",
        json=payload,
        headers={"access-token": "my-token"},
    )
    assert res.status_code == 422
    res = client.put(
        "/api/storage/stats/example-project/databrowser/0/",
        json={"query.project": "cmip5"},
        headers={"access-token": "my-token"},
    )
    assert res.status_code == 200
    res = client.put(
        "/api/storage/stats/tests/databrowser/0",
        json=payload,
        headers={"access-token": "my-token"},
    )
    assert res.status_code == 401
    res = client.put(
        "/api/storage/stats/tests/databrowser/0",
        json={"metadata.num_results": 2},
        headers={"access-token": access_token},
    )
    assert res.status_code == 500
    for keys in (
        payload,
        {"query.foo": "bar"},
        {"query.project": 3},
        {"metadata": {"num_results": 2}},
        {"metadata.num_results": "foo"},
        {"metadata.foo": "bar"},
    ):
        res = client.put(
            "/api/storage/stats/example-project/databrowser/0",
            json=keys,
            headers={"access-token": access_token},
        )
        assert res.status_code == 422

    res = client.put(
        f"/api/storage/stats/example-project/databrowser/{uuid4().hex[:24]}",
        json={"metadata": stats["metadata"], "query": stats["query"]},
        headers={"access-token": access_token},
    )
    assert res.status_code == 304


@pytest.mark.asyncio
async def test_put_search_method_success(
    client: TestClient,
    databrowser_search_stats: List[Dict[str, Any]],
    access_token: str,
    mongo_databrowser_collection: int,
) -> None:
    """Test the put method."""
    stats = databrowser_search_stats[0].copy()
    payload = {"metadata": stats["metadata"], "query": stats["query"]}
    payload["metadata"]["num_results"] = 999
    res = client.put(
        f"/api/storage/stats/example-project/databrowser/{stats['_id']}/",
        json=payload,
        headers={"access-token": "my-token"},
    )
    assert res.status_code == 200
    res = client.post(
        "/api/storage/stats/tests/databrowser",
        json={"metadata": stats["metadata"], "query": stats["query"]},
        headers={"access-token": access_token},
    )
    key = res.json()["id"]

    res = client.put(
        f"/api/storage/stats/tests/databrowser/{key}",
        json={"metadata": stats["metadata"], "query": stats["query"]},
        headers={"access-token": access_token},
    )
    assert res.status_code == 200
    res = client.put(
        f"/api/storage/stats/tests/databrowser/{key}",
        json={"metadata.num_results": 20, "query.project": "cmip5"},
        headers={"access-token": access_token},
    )
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_delete_method(
    client: TestClient,
    databrowser_search_stats: List[Dict[str, Any]],
    access_token: str,
) -> None:
    """Test the delete method."""
    res = client.delete(
        "/api/storage/stats/example-project/databrowser/0",
        headers={"access-token": "my-token"},
    )
    assert res.status_code == 204
    res = client.delete("/api/storage/stats/tests/databrowser/0")
    assert res.status_code == 401
    res = client.delete(
        "/api/storage/stats/tests/databrowser/0",
        headers={"access-token": access_token},
    )
    assert res.status_code == 500
    res = client.delete(
        f"/api/storage/stats/tests/databrowser/{uuid4().hex[:24]}",
        headers={"access-token": access_token},
    )
    assert res.status_code == 404
    stats = databrowser_search_stats[0].copy()
    res = client.post(
        "/api/storage/stats/tests/databrowser",
        json={"metadata": stats["metadata"], "query": stats["query"]},
        headers={"access-token": access_token},
    )
    key = res.json()["id"]
    res = client.delete(
        f"/api/storage/stats/tests/databrowser/{key}",
        headers={"access-token": access_token},
    )
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_get_search_method_unauthorised(client: TestClient) -> None:
    """Test the get statistics method."""
    res = client.get("/api/storage/stats/tests/databrowser")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_search_method_authorised(
    client: TestClient,
    access_token: str,
    mongo_databrowser_collection: int,
    databrowser_search_stats: List[Dict[str, Any]],
) -> None:
    """Test the get statistics method."""
    res = client.get(
        "/api/storage/stats/tests/databrowser",
    )
    assert res.status_code == 401
    res = client.get(
        "/api/storage/stats/example-project/databrowser",
        headers={"access-token": "my-token"},
    )
    assert res.status_code != 401
    res = client.get(
        "/api/storage/stats/tests/databrowser",
        headers={"access-token": access_token},
    )
    assert res.status_code == 200
    assert len(list(res.iter_lines())) == mongo_databrowser_collection + 1
    res = client.get(
        "/api/storage/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"num_results": 0, "before": "2020-02-02"},
    )
    assert res.status_code == 404
    res = client.get(
        "/api/storage/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"server_status": 500},
    )
    assert res.status_code == 404
    res = client.get(
        "/api/storage/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"num_results": 0, "after": "foo"},
    )
    assert res.status_code == 200
    assert len(list(res.iter_lines())) == mongo_databrowser_collection + 1
    res = client.get(
        "/api/storage/stats/tests/databrowser",
        headers={"access-token": access_token},
        params={"project": "cmip"},
    )
    assert res.status_code == 200
