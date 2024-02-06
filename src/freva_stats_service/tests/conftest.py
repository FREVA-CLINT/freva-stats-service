"""Definition of pytest fixtures."""

import os
from copy import copy
from datetime import datetime
from typing import Any, Dict, Iterator, List

import pytest
from fastapi.testclient import TestClient
from pymongo.mongo_client import MongoClient

from freva_stats_service.run import app  # type: ignore
from freva_stats_service.tests import read_gunzipped_stats
from freva_stats_service.utils import mongo_client


@pytest.fixture(scope="function")
def mongo_databrowser_collection() -> Iterator[int]:
    """Set up mongo connection."""
    databrowser_search_stats = read_gunzipped_stats(
        "databrowser-stats.json.gz"
    )
    with MongoClient(mongo_client.mongo_url) as m_client:  # type: ignore
        collection = m_client["tests"]["search_queries"]
        try:
            collection.delete_many({})
            for i, data in enumerate(copy(databrowser_search_stats)):
                if i != 9:
                    data["metadata"]["date"] = datetime.fromisoformat(
                        data["metadata"]["date"]
                    )
                collection.insert_one(
                    {"metadata": data["metadata"], "query": data["query"]}
                )
                if i == 9:
                    break
            yield 10
        finally:
            collection.delete_many({})


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Set up the test client for the unit test."""
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        for collection in ("search_queries",):
            MongoClient(mongo_client.mongo_url)["tests"][
                collection
            ].delete_many({})


@pytest.fixture(scope="session")
def databrowser_search_stats() -> Iterator[List[Dict[str, Any]]]:
    """Add search search statistics to the mongoDB instance."""
    yield read_gunzipped_stats("databrowser-stats.json.gz")


@pytest.fixture(scope="session")
def access_token() -> Iterator[str]:
    """Create an access token."""
    with TestClient(app) as test_client:
        res = test_client.post(
            "/api/token",
            data={
                "password": os.environ["API_PASSWORD"],
                "username": os.environ["API_USERNAME"],
            },
            params={"expires_in": -1},
        )
        yield res.json()["access_token"]
