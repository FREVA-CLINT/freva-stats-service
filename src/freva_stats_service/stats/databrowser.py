"""Collection of statistics methods."""

import datetime
from typing import Annotated, Any, Dict, Literal, Optional, Union

from fastapi import Body, Header, HTTPException, Path, Query, Request, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Required

from ..app import app
from ..response import databrowser_stats_csv_stream
from ..utils import (
    get_date_query,
    get_query_params,
    insert_mongo_db_data,
    logger,
    mongo_client,
    validate_databrowser_stats,
    validate_token,
)

__all__ = [
    "add_databrowser_stats",
    "query_databrowser",
    "replace_databrowser_stats",
]


class DataBrowserStatsModel(BaseModel):
    """Stats model for saving databrowser search statistics."""

    metadata: Dict[str, Union[int, str, datetime.datetime]]
    query: Dict[str, str]


@app.post(
    "/api/stats/{project_name}/databrowser",
    status_code=status.HTTP_201_CREATED,
    tags=["Freva Statistics"],
)
async def add_databrowser_stats(
    project_name: Annotated[
        str,
        Path(
            description="Name of the freva instance for gathering information.",
            example="docs",
        ),
    ],
    payload: DataBrowserStatsModel,
    access_token: Annotated[
        str,
        Header(
            description="Token for authentication",
            example="faketoken",
        ),
    ] = "",
) -> Dict[str, str]:
    """Add new statistics to the databrowser stats."""
    logger.debug("Validating token: %s", access_token)
    if project_name == "docs" and access_token == "faketoken":
        return {"status": "Data created successfully"}
    await validate_token(access_token)
    data = payload.dict()
    logger.debug("Validating data for %s:", payload)
    await validate_databrowser_stats(data)
    data["metadata"]["date"] = datetime.datetime.now(tz=datetime.timezone.utc)
    logger.debug("Adding payload: %s to DB.", payload)
    await insert_mongo_db_data(project_name, "search_queries", **data)
    return {"status": "Data created successfully"}


@app.put(
    "/api/stats/{project_name}/databrowser/{stat_id}",
    status_code=status.HTTP_200_OK,
    tags=["Freva Statistics"],
)
async def replace_databrowser_stats(
    project_name: Annotated[
        str,
        Path(
            description="Name of the freva instance for gathering information.",
            example="docs",
        ),
    ],
    stat_id: Annotated[
        str, Path(description="The DB index that shall be replaced.")
    ],
    payload: DataBrowserStatsModel,
    access_token: Annotated[
        str,
        Header(
            description="Token for authentication",
            example="faketoken",
        ),
    ] = "",
) -> Dict[str, str]:
    """Replace existing statistics in the database."""
    if project_name == "docs" and access_token == "faketoken":
        return {"status": "Data created successfully"}
    logger.debug("Validating token: %s", access_token)
    await validate_token(access_token)
    data = payload.dict()
    logger.debug("Validating data for %s:", payload)
    await validate_databrowser_stats(data)
    logger.debug("Updating payload for ID %s: %s to DB.", stat_id, payload)
    await insert_mongo_db_data(
        project_name, "search_queries", key=stat_id, **data
    )
    return {"status": "Data updated successfully"}


@app.get("/api/stats/{project_name}/databrowser", tags=["Freva Statistics"])
async def query_databrowser(
    project_name: Annotated[
        str,
        Path(
            description="Name of the freva instance for gathering information.",
            example="docs",
        ),
    ],
    num_results: Annotated[
        Optional[int],
        Query(
            description="Number of results",
            ge=0,
            example=0,
        ),
    ] = None,
    results_operator: Annotated[
        Literal["gte", "lte", "gt", "lt", "eq"],
        Query(description="Comparison operator for 'num_results'"),
    ] = "gte",
    flavour: Annotated[
        Optional[str],
        Query(
            description="Subset the databrowser flavour the users were using.",
            example="freva",
        ),
    ] = None,
    uniq_key: Annotated[
        Optional[str],
        Query(
            description=(
                "Subset the unique key parameter (file, uri) the users"
                "were using."
            ),
        ),
    ] = None,
    server_status: Annotated[
        Optional[int],
        Query(
            description=(
                "Look only for searches that had a certain server "
                "response status."
            ),
            ge=0,
        ),
    ] = None,
    before: Annotated[
        Optional[str],
        Query(
            description="timestamp: Select only results added BEFORE this timestamp",
        ),
    ] = None,
    after: Annotated[
        Optional[str],
        Query(
            description="timestamp: Select only results added AFTER this timestamp",
        ),
    ] = None,
    project: Annotated[
        Optional[str],
        Query(
            description="Subset the statistics based on <project> name.",
            example="cmip",
        ),
    ] = None,
    product: Annotated[
        Optional[str],
        Query(description="Subset the statistics based on <product> name."),
    ] = None,
    model: Annotated[
        Optional[str],
        Query(description="Subset the statistics based on <model> name."),
    ] = None,
    institute: Annotated[
        Optional[str],
        Query(
            description="Subset the statistics based on <institute> name.",
        ),
    ] = None,
    experiment: Annotated[
        Optional[str],
        Query(
            description="Subset the statistics based on <experiment> name.",
        ),
    ] = None,
    variable: Annotated[
        Optional[str],
        Query(
            description="Subset the statistics based on <variable> name.",
            example="tas",
        ),
    ] = None,
    time_frequency: Annotated[
        Optional[str],
        Query(
            description="Subset the statistics based on <time_frequency> name.",
        ),
    ] = None,
    ensemble: Annotated[
        Optional[str],
        Query(description="Subset the statistics based on <ensemble> name."),
    ] = None,
    realm: Annotated[
        Optional[str],
        Query(description="Subset the statistics based on <realm> name."),
    ] = None,
    access_token: Annotated[
        str,
        Header(description="Token for authentication", example="faketoken"),
    ] = "",
) -> StreamingResponse:
    """Filter for user databrowser queries.

    Instead of filtering user databrowser queries yourself you
    can make a pre selection of user queries. For exampmle you
    can only retrieve user searches for a given project or
    combinations of a model and a variable.

    """
    logger.debug("Validating token: %s", access_token)
    if project_name != "docs" and access_token != "faketoken":
        await validate_token(access_token)
    query_filters = {
        "project": project,
        "product": product,
        "model": model,
        "variable": variable,
        "institute": institute,
        "experiment": experiment,
        "time_frequency": time_frequency,
        "ensemble": ensemble,
        "realm": realm,
    }

    mongo_query: Dict[str, Any] = {
        f"metadata.{k}": {"$regex": v, "$options": "ix"}
        for (k, v) in zip(
            ("num_results", "flavour", "uniq_key"),
            (num_results, flavour, uniq_key),
        )
        if v is not None
    }
    if num_results is not None:
        mongo_query["metadata.num_results"] = {
            f"${results_operator}": num_results
        }
    if server_status is not None:
        mongo_query["metadata.num_results"] = server_status
    date_query = await get_date_query(before, after)
    if date_query:
        mongo_query["metadata.date"] = date_query
    for key, value in query_filters.items():
        if value is not None:
            mongo_query[f"query.{key}"] = {"$regex": value, "$options": "ix"}
    count = await mongo_client[
        f"{project_name}.search_queries"
    ].count_documents(mongo_query)
    if count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results for query, check query parameters.",
        )
    return StreamingResponse(
        databrowser_stats_csv_stream(project_name, mongo_query),
        status_code=200,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=databrowser.csv",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        },
    )
