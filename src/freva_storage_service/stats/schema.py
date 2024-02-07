"""Definition of all input schemas."""

from typing import Annotated, Dict, Literal, Optional

from pydantic import BaseModel, Field


class MetaDataStatsModel(BaseModel):
    """Schema for the metadata."""

    num_results: Annotated[
        int, Field(..., description="The number of results", example=10)
    ]
    flavour: Annotated[
        str,
        Field(
            ...,
            description="Search flavour utilised by the users",
            example="freva",
        ),
    ]
    uniq_key: Annotated[
        Literal["file", "uri"],
        Field(
            ...,
            description="Unique key (either 'file' or 'uri').",
            example="file",
        ),
    ]
    server_status: Annotated[
        int, Field(..., description="Server status code.", example=200)
    ]
    date: Optional[
        Annotated[
            str,
            Field(
                None,
                description="Timestamp when the statistics have been added.",
                example="2024-01-30T12:34:56",
            ),
        ]
    ]


class DataBrowserStatsModel(BaseModel):
    """Stats model for saving databrowser search statistics."""

    metadata: Annotated[
        MetaDataStatsModel,
        Field(..., description="Metadata for the statistics."),
    ]
    query: Annotated[
        Dict[str, str],
        Field(
            ...,
            description="A sub set of the user's search queries.",
            example={"project": "cmip6"},
        ),
    ]
