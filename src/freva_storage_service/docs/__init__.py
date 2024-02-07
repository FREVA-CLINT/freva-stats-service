"""Collection of datasets for documentation purpose."""

import gzip
import json
from datetime import datetime
from pathlib import Path
from typing import cast

from ..utils import mongo_client


async def add_databrowser_stats(db_name: str) -> int:
    """Add example data for the databrowser query statistics."""
    archive_path = Path(__file__).parent / "databrowser-stats.json.gz"
    collection = mongo_client[f"{db_name}.search_queries"]
    with gzip.open(archive_path, "rt") as gzip_file:
        queries = json.loads(gzip_file.read())
    await collection.delete_many({})
    for query in queries:
        query["metadata"]["date"] = datetime.fromisoformat(query["metadata"]["date"])
        await collection.insert_one(query)
    return cast(int, await collection.count_documents({}))


async def start_up(db_name: str = "example-project") -> None:
    """Define startup behaviour."""
    try:
        await add_databrowser_stats(db_name)
    except Exception:
        pass
