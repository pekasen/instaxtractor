"""Test suite for the data extraction and alignment functions we'll utilize for
getting data out of the HARs as lean and HQ as possible.

Our package should be able to retrieve data from Instagram HARs in a way that is:

- fast.
- output is as small as possible, e.g. get only the media data that belong to the
  metadata we are interested in.
- reliable, as in if Instagram suddenly has the idea to change their data structure
  we should be able to react without changing code. Thus, we should use configuration
  files to notate what to extract from where and when.
"""
import math
import random
from pathlib import Path
from typing import Any, Dict

import pytest
import ujson

from instaxtractor.extract import MIMEType, Predicate, extract


@pytest.fixture()
def har() -> Dict[str, Any]:
    """Get stub data as well as expectations.

    Returns:
        Dict[str, Any] : A HAR file
    """
    files = list(Path("tests/stubs").glob("*.har"))
    #  load a random stub JSON/HAR file
    file_number = math.floor(random.random() * (len(files) - 1))
    #  return that to the test
    with files[file_number].open("r", encoding="utf8") as file:
        return ujson.load(file)


@pytest.mark.parametrize(
    "predicate,expected",
    [
        (Predicate(MIMEType.JPEG, None), "Hi, I am a JPEG."),
        (Predicate(MIMEType.MP4, None), "Hi, I am a MP4 video."),
        (Predicate(MIMEType.JSON, None), "Hi, I am a JSON file."),
        (Predicate(None, "api/v1"), "Hi, I am a JPEG."),
        (Predicate(MIMEType.JPEG, "api/v1"), "Hi, I am a JPEG."),
    ],
)
def test_extractor(predicate, expected):  # pylint: disable=W0621
    """The extractor takes a Dict and a predicate where we want to extract data at.

    Params:
        har : Dict[str, Any]
    """
    with Path("tests/stubs/test_1_minimal.har").open("r", encoding="utf8") as file:
        _har = ujson.load(file)

    assert extract(_har, predicate)[0]["response"]["content"]["text"] == expected
