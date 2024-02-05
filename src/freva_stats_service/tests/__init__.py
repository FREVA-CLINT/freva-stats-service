"""Unit tests."""

import gzip
import json
from pathlib import Path
from typing import Any, Dict, List, cast

from freva_stats_service import docs


def read_gunzipped_stats(file_name: str) -> List[Dict[str, Any]]:
    """Read data in a gunzipped json file."""

    archive_path = Path(docs.__file__).parent / file_name
    with gzip.open(archive_path, "rt") as gzip_file:
        return cast(List[Dict[str, Any]], json.loads(gzip_file.read()))
