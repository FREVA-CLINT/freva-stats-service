"""Main script that runs the rest API."""
from urllib.parse import parse_qsl

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import Required

from .app import app
from .docs import start_up
from .response import TokenResponse
from .stats import *
from .utils import (
    create_oauth_token,
    get_oauth_credentials,
    logger,
    mongo_client,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Close the MongoDB connection on application shutdown."""

    mongo_client.close()


@app.on_event("startup")
async def startup_event() -> None:
    """Call a bunch of functions on startup."""
    await start_up("docs")


# Route to get an OAuth2 token
@app.post("/api/token", tags=["Authentication"])
async def login_for_access_token(
    credentials: OAuth2PasswordRequestForm = Depends(),
    request: Request = Required,
) -> JSONResponse:
    """Create an oauth token from login credentials."""
    oauth_credentials = await get_oauth_credentials()
    if (
        credentials.username != oauth_credentials["username"]
        or credentials.password != oauth_credentials["password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expiry = 1
    try:
        for key, value in parse_qsl(str(request.query_params)):
            if key == "expires_in":
                expiry = int(value)
                break
    except Exception:
        pass
    token, expires_at = await create_oauth_token(credentials.username, expiry)
    return JSONResponse(
        content={
            "access_token": token,
            "expires_at": expires_at,
            "token_type": "bearer",
        },
        status_code=status.HTTP_201_CREATED,
    )
