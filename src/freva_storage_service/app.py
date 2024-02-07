"""The freva storage restAPI 🚀

The freva storage restAPI is a powerful interface designed to interact with a
database storage systems, providing functionalities to store, query, and
manage statistical data related to user searches in the freva application.
It is designed with security, flexibility, and ease of use in mind.

Currently the following functionality is implemented:

- add, retrieve, delete databrowser user search queries.
- add, retrieve, delete freva plugin statistics (work in progress).


Authentication
--------------
The API supports token-based authentication using OAuth2. To obtain an access
token, clients can use the `/api/storage/v2/token` endpoint by providing valid
username and password credentials. The access token should then be included in
the Authorization header for secured endpoints.

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
from .utils import logger  # noqa: F401

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

print(bool(int(os.environ["DEBUG"])))
app = FastAPI(
    debug=bool(int(os.environ["DEBUG"])),
    title="Freva storage restAPI",
    description=__doc__,
    openapi_url="/api/storage/docs/openapi.json",
    docs_url="/api/storage/docs",
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
