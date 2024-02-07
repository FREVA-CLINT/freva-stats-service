"""Collection of statistics methods."""

import datetime
from typing import Annotated, Any, Dict, Literal, Optional, Union

import bson
from fastapi import Header, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse, Response, StreamingResponse
from pydantic import BaseModel

from ..app import app
from ..response import databrowser_stats_csv_stream
from ..utils import (
    get_date_query,
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
    "/api/storage/stats/{project_name}/databrowser",
    status_code=status.HTTP_201_CREATED,
    tags=["Freva Statistics"],
)
async def add_databrowser_stats(
    project_name: Annotated[
        str,
        Path(
            description="Name of the freva instance for gathering information.",
            example="example-project",
        ),
    ],
    payload: DataBrowserStatsModel,
) -> Dict[str, str]:
    """Add new statistics to the databrowser stats."""
    if project_name == "example-project":
        return {"status": "Data created successfully"}
    data = {k: v for (k, v) in payload.dict().items() if v is not None}
    logger.debug("Validating data for %s:", data)
    await validate_databrowser_stats(data)
    data["metadata"]["date"] = datetime.datetime.now(tz=datetime.timezone.utc)
    logger.debug("Adding payload: %s to DB.", data)
    key = await insert_mongo_db_data(project_name, "search_queries", **data)
    return {
        "status": "Data created successfully",
        "id": str(key),
    }


@app.put(
    "/api/storage/stats/{project_name}/databrowser/{stat_id}",
    tags=["Freva Statistics"],
)
async def replace_databrowser_stats(
    project_name: Annotated[
        str,
        Path(
            description="Name of the freva instance for gathering information.",
            example="example-project",
        ),
    ],
    stat_id: Annotated[
        str,
        Path(
            description="The DB index that shall be replaced.",
            example="1fc3fa0b5a854d21856d4bff",
        ),
    ],
    payload: Dict[str, Any],
    access_token: Annotated[
        str,
        Header(
            description="Token for authentication",
            example="my-token",
        ),
    ] = "",
) -> JSONResponse:
    """Replace existing statistics in the database."""
    if project_name == "example-project" and access_token == "my-token":
        return JSONResponse(
            {"status": "Data updated successfully"},
            status_code=status.HTTP_200_OK,
        )
    logger.debug("Validating token: %s", access_token)
    await validate_token(access_token)
    data = {k: v for (k, v) in payload.items() if v is not None}
    logger.debug("Validating data for %s:", data)
    await validate_databrowser_stats(data, method="put")
    logger.debug("Updating payload for ID %s: %s to DB.", stat_id, data)
    _ = await insert_mongo_db_data(
        project_name, "search_queries", key=stat_id, **data
    )
    return JSONResponse(
        {"status": "Data updated successfully"}, status_code=status.HTTP_200_OK
    )


@app.get(
    "/api/storage/stats/{project_name}/databrowser", tags=["Freva Statistics"]
)
async def query_databrowser(
    project_name: Annotated[
        str,
        Path(
            description="Name of the freva instance for gathering information.",
            example="example-project",
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
        Header(description="Token for authentication", example="my-token"),
    ] = "",
) -> StreamingResponse:
    """Filter for user databrowser queries.

    Instead of filtering user databrowser queries yourself you
    can make a pre selection of user queries. For exampmle you
    can only retrieve user searches for a given project or
    combinations of a model and a variable.

    This GET method returns a csv data stream. This enables users to
    read the data by data analysis tools like ``pandas`` to do more in
    depth analytics. For example:


        import io
        import requests
        import pandas as pd

        res = requests.get(
            "http://example.com/api/storage/stats/my-project/databrowser",
            headers={"access-token": "my-token"},
        )
        csv_content = io.BytesIO()
        for chunk in res.iter_content(chunk_size=8192):
             csv_content.write(chunk)
        csv_content.seek(0)
        df = pd.read_csv(csv_content, index_col=0)

    """
    if project_name != "example-project" and access_token != "my-token":
        logger.debug("Validating token: %s", access_token)
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


@app.delete(
    "/api/storage/stats/{project_name}/databrowser/{stat_id}",
    tags=["Freva Statistics"],
)
async def delete_statistics_by_index(
    project_name: Annotated[
        str,
        Path(
            description="Name of the freva instance for gathering information.",
            example="example-project",
        ),
    ],
    stat_id: Annotated[
        str,
        Path(
            description="The DB index that shall be replaced.",
            example="1fc3fa0b5a854d21856d4bff",
        ),
    ],
    access_token: Annotated[
        str,
        Header(description="Token for authentication", example="my-token"),
    ] = "",
) -> Response:
    """Delete existing statistics in the database by a given key."""
    if project_name == "example-project" and access_token == "my-token":
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    logger.debug("Validating token")
    await validate_token(access_token)
    logger.debug("Deleting item")
    try:
        _id = bson.objectid.ObjectId(stat_id)
    except bson.errors.InvalidId as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invalid id: {stat_id}",
        ) from error
    result = await mongo_client[f"{project_name}.search_queries"].delete_one(
        {"_id": _id}
    )
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{stat_id} not found.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
