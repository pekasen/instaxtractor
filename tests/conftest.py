"""fixture parking space"""

from pathlib import Path
from typing import Any, Dict

import pytest
import ujson


@pytest.fixture(params=list(Path("tests/stubs").glob("*.har")))
def har(request) -> Dict[str, Any]:
    """Get stub data as well as expectations.

    Returns:
        Dict[str, Any] : A HAR file
    """
    file = request.param
    #  load a random stub JSON/HAR file
    #  return that to the test
    with file.open("r", encoding="utf8") as json_file:
        return ujson.load(json_file)
