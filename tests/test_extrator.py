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

from pathlib import Path

import pytest
import ujson

from instaxtractor.extract import MIMEType, Predicate, extract, pluck


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
def test_extractor(predicate, expected):
    """The extractor takes a Dict and a predicate where we want to extract data at.

    Params:
        har : Dict[str, Any]
    """
    with Path("tests/stubs/test_1_minimal.har").open("r", encoding="utf8") as file:
        _har = ujson.load(file)

    assert extract(_har, predicate)[0]["response"]["content"]["text"] == expected


@pytest.mark.parametrize(
    "test_input,spec,expected",
    [
        ({"a": {"b": 1}}, {"c": ["a", "b"]}, {"c": 1}),
        (
            {"a": {"b": 1, "f": 123}},
            {"c": ["a", "b"], "g": ["a", "f"]},
            {"c": 1, "g": 123},
        ),
    ],
)
def test_pluck(test_input, spec, expected):
    """should extract data from the dict as specified"""
    assert pluck(test_input, spec) == expected
