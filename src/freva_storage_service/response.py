"""Collection of response models."""

from datetime import datetime
from typing import Any, AsyncIterator, Dict, Tuple

from databrowser.core import Translator
from pydantic import BaseModel

from .utils import logger, mongo_client


class TokenResponse(BaseModel):
    """Definition of the response that sends the created token."""

    access_token: str
    expires_at: int
    token_type: str = "bearer"


async def databrowser_stats_csv_stream(
    db_name: str,
    mongo_query: Dict[str, Any],
) -> AsyncIterator[str]:
    """Create a csv stream from a mongo search query.

    Parameters
    ----------
    db_name: str
        Name of the mongo db that is queried.
    mongo_query: dict
        Mongo search query.

    Yields
    ------
    str: csv representation of the search result.
    """
    facet_keys = tuple(Translator("freva").valid_facets)
    header: Tuple[str, ...] = ()
    logger.debug("Apply mongoDB search query %s", mongo_query)
    async for document in mongo_client[f"{db_name}.search_queries"].find(
        mongo_query
    ):
        result = {**{"id": document["_id"]}, **document["metadata"].copy()}
        if isinstance(result.get("date"), datetime):
            result["date"] = result["date"].isoformat()
        if not header:
            header = tuple(result.keys()) + tuple(facet_keys)
            yield ",".join(header) + "\n"
        for facet in facet_keys:
            result[facet] = document["query"].get(facet, "")
        yield ",".join(map(str, result.values())) + "\n"
