"""The freva storage restAPI 🚀

The freva storage restAPI is a powerful interface designed to interact with a
database storage systms, providing functionalities to store, query, and
manage statistical data related to user searches in the freva application.
It is designed with security, flexibility, and ease of use in mind.

Currently the following functionality is implemented:

- add, retrieve, delete databrowser user search queries.
- add, retrieve, delete freva plugin statistics.


Authentication
--------------
The API supports token-based authentication using OAuth2. To obtain an access
token, clients can use the `/api/token` endpoint by providing valid username and
password credentials. The access token should then be included in the
Authorization header for secured endpoints.

Data Validation
---------------
Data payloads are validated using JSON Schema to ensure the correct
structure and types. The validation prevent unauthorized access
or invalid inputs.

Overview
--------
"""

import os

from fastapi import FastAPI

from ._version import __version__
from .utils import logger

metadata_tags = [
    {
        "name": "Authentication",
        "description": "Create tokens for authentication.",
    },
    {
        "name": "Freva Statistics",
        "description": "Get, Post, Delete freva statistics",
    },
]

app = FastAPI(
    debug=bool(int(os.environ.get("DEBUG", "0"))),
    title="Freva storage restAPI",
    description=__doc__,
    openapi_url="/api/docs/openapi.json",
    docs_url="/api/docs",
    redoc_url=None,
    openapi_tags=metadata_tags,
    version=__version__,
    summary="Freva statistics API.",
    contact={"name": "DKRZ, Clint", "email": "freva@dkrz.de"},
    license_info={
        "name": "BSD 2-Clause License",
        "url": "https://opensource.org/license/bsd-2-clause",
    },
)
