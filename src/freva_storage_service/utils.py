"""Collection of utility functions."""

import hashlib
import os
from datetime import datetime, timedelta, timezone
from functools import cached_property
from typing import (
    Any,
    Dict,
    List,
    Literal,
    NotRequired,
    Optional,
    Tuple,
    TypedDict,
    Union,
)

from bson.errors import InvalidId
from bson.objectid import ObjectId
from databrowser.core import Translator
from dateutil.parser import ParserError
from dateutil.parser import parse as parse_time
from fastapi import HTTPException, status
from jose import JWTError, jwt
from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from motor.motor_asyncio import AsyncIOMotorClient

from .logger import Logger

logger = Logger(debug=bool(int(os.environ.get("DEBUG", "0"))))


CredentialsType = TypedDict(
    "CredentialsType", {"password": str, "username": str}
)

SchemaType = TypedDict(
    "SchemaType",
    {
        "type": str,
        "properties": Dict[str, Any],
        "required": NotRequired[List[str]],
        "additionalProperties": bool,
    },
)


class MongoDB:
    """A helper class that handles different mongoDB connection instances."""

    def __init__(self) -> None:
        self._mongo_client: Any = AsyncIOMotorClient(
            self.mongo_url, serverSelectionTimeoutMS=5000
        )

    def __getitem__(self, key: str) -> Any:
        db, _, collection = key.partition(".")
        return self._mongo_client[db][collection]

    def close(self) -> None:
        """Disconnect from mongodb."""

        try:
            self._mongo_client.close()
        except Exception as error:  # pragma: no cover
            logger.critical("Could not shutdown mongodb connection: %s", error)

    @cached_property
    def mongo_url(self) -> str:
        """Construct the url to the mongodb from environment variables."""
        host = os.environ["MONGO_HOST"]
        host, _, m_port = host.partition(":")
        port = m_port or "27017"
        user = os.environ["MONGO_USERNAME"]
        passwd = os.environ["MONGO_PASSWORD"]
        return f"mongodb://{user}:{passwd}@{host}:{port}"


async def define_secret_key() -> str:
    """Define the secret key for the web token."""
    return hashlib.sha256(
        (os.environ["API_USERNAME"] + os.environ["API_PASSWORD"]).encode(
            "utf-8"
        )
    ).hexdigest()


async def create_oauth_token(
    username: str, expiry: int = 1
) -> Tuple[str, Optional[int]]:
    """Create an OAuth2 web token.

    Parameters
    ----------
    username: str
        The username payload
    expiry: str
        Set the expiry date of the token in days from now.
        setting a negative number of days will result in an
        non-expirying token
    """
    payload: Dict[str, Union[str, int, None]] = {"sub": username}
    if expiry > -1:
        exp = int((datetime.utcnow() + timedelta(days=1)).timestamp())
        payload["exp"] = exp
    else:
        exp = None

    token = jwt.encode(
        payload.copy(), await define_secret_key(), algorithm="HS256"
    )
    return token, exp


async def get_date_query(
    before: Optional[str] = None, after: Optional[str] = None
) -> Dict[str, datetime]:
    """Create a mongo query for dates."""
    query = {}
    defaults = (datetime(1, 1, 1, 0, 0, 0), datetime(9999, 12, 31, 23, 59, 59))
    for num, (timestamp, operator) in enumerate(
        zip((before, after), ("$lte", "$gte"))
    ):
        if timestamp is not None:
            try:
                t_step = parse_time(timestamp, default=defaults[num])
            except ParserError:
                logger.warning("Could not parse timestamp %s", timestamp)
                continue
            query[operator] = t_step.astimezone(timezone.utc)

    return query


async def get_oauth_credentials() -> CredentialsType:
    """Read the oauth login credentials from the environemnt variables."""
    return {
        "username": os.environ["API_USERNAME"],
        "password": os.environ["API_PASSWORD"],
    }


async def insert_mongo_db_data(
    db_name: str,
    collection_name: str,
    key: Optional[str] = None,
    **data: Any,
) -> str:
    """Insert data into a mongoDB collection.

    Parameters
    ----------
    db_name: str
        The name of the mongodb
    collection_name: str
        The name of the mongoDB collection where the data should be added to.
    key: str, default: None
        If a collection key is given the data is updated rathen than a new
        entry created. If no key is given (default) a new entry is created.
    **data: Any
        The data that is added to the mongoDB collection.

    Returns
    -------
    str: the inserted key.

    Raises
    ------
    HTTPException: If connection to mongo_db failed.
    """
    if key is None:
        coro = mongo_client[f"{db_name}.{collection_name}"].insert_one(data)
    else:
        try:
            coro = mongo_client[f"{db_name}.{collection_name}"].update_one(
                {"_id": ObjectId(key)}, {"$set": data}
            )
        except InvalidId as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid ID",
            ) from error
    result = await coro
    if key is None:
        key = result.inserted_id
    else:
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_304_NOT_MODIFIED,
                detail="No changes were made to the item",
            )
    return key


async def validate_databrowser_stats(
    data: Dict[str, Union[Dict[str, Union[str, int]], str, int]],
    method: Literal["post", "put", "del"] = "post",
) -> None:
    """Check if the databrowser metadata schema is valid.

    Parameters
    ----------
    data: dict
        The dict containing the databrowser search stats.
    method: str
        Which update/insert method is applied.

    Raises
    ------
    HTTPException: If the metadata scheme is unvalid 422 error is risen.
    """
    facet_keys = tuple(Translator("freva").valid_facets)
    query_schema: SchemaType = {
        "type": "object",
        "properties": {key: {"type": "string"} for key in facet_keys},
        "additionalProperties": False,
    }
    metadata_schema: SchemaType = {
        "type": "object",
        "properties": {
            "num_results": {"type": "integer"},
            "flavour": {"type": "string"},
            "uniq_key": {"type": "string"},
            "server_status": {"type": "integer"},
            "date": {"type": "string"},
        },
        "required": ["num_results", "flavour", "uniq_key", "server_status"],
        "additionalProperties": False,
    }
    schema: SchemaType = {
        "type": "object",
        "properties": {"metadata": metadata_schema, "query": query_schema},
        "additionalProperties": False,
    }
    if method == "post":
        schema["required"] = ["metadata", "query"]
    else:
        if "metadata" not in data:
            del schema["properties"]["metadata"]["required"]
        schema["properties"].update(
            {
                **{
                    f"metadata.{k}": v
                    for k, v in metadata_schema["properties"].items()
                },
                **{
                    f"query.{k}": v
                    for k, v in query_schema["properties"].items()
                },
            }
        )
    try:
        validate(data, schema)
    except JsonSchemaValidationError as error:
        logger.error("Metadata validation failed: %s", error)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Metadata validation failed",
        ) from error


async def validate_token(access_token: str) -> None:
    """Validate a given access token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        _ = jwt.decode(
            access_token, await define_secret_key(), algorithms=["HS256"]
        )
    except JWTError:
        raise credentials_exception


mongo_client = MongoDB()
