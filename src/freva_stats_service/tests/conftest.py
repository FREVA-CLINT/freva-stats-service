"""Definition of pytest fixtures."""

import os
from typing import Iterator

from fastapi.testclient import TestClient
from pymongo.mongo_client import MongoClient
import pytest

from freva_stats_service.run import app
from freva_stats_service.utils import mongo_client
from freva_stats_service.tests import read_gunzipped_stats


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Setup the test client for the unit test."""
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        for collection in ("search_queries",):
            MongoClient(mongo_client.mongo_url)["tests"][collection].delete_many({})


@pytest.fixture(scope="module")
def databrowser_search_stats() -> Iterator[int]:
    """Add search search statistics to the mongoDB instance."""
    yield read_gunzipped_stats("databrowser-stats.json.gz")


@pytest.fixture(scope="session")
def access_token(client: TestClient) -> Iterator[str]:
    """Create an access token."""
    res = client.post(
        "/api/token",
        data={
            "password": os.environ["API_PASSWORD"],
            "username": os.environ["API_USERNAME"],
        },
        params={"expires_in": -1},
    )
    yield res.json()["access_token"]
