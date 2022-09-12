"""main business logic for extracting content

Constants:

    ENTRIES : List[str]
        accessor path for the entries list in a HAR file

    MIMETYPE : List[str]
        accessor path for the mime type in a log entry

    URL : List[str]
        accessor path for the url in a log entry
"""

import dataclasses
from functools import reduce
from typing import Any, Dict, List, Optional

ENTRIES = ["log", "entries"]
MIMETYPE = ["response", "content", "mimeType"]
URL = ["request", "url"]


def _deep_access_(data: Dict[str, Any], path: List[str]) -> Optional[Any]:
    def _reducer_(carry: Optional[Dict[str, Any]], key: str):
        if carry:
            return carry.get(key)
        return None

    return reduce(_reducer_, path, data)


class MIMEType:  # pylint: disable=R0903
    """Wrapper for MIMETypes"""

    JPEG = "image/jpeg"
    PNG = "image/png"
    MP4 = "video/mp4"
    JSON = "application/json"


@dataclasses.dataclass
class Predicate:
    """Formulates a query against the HAR data structure"""

    mimetype: Optional[str]
    url_fragment: Optional[str]


def match(data: Dict[str, Any], predicate: Predicate) -> bool:
    """return whether given data object mathes the predicate

    Params:
        data : Dict[str, Any]
            the data to process
        predicate : Predicate
            the predicate to match the data against

    Returns:
        bool : if the record is valied and matches the predicate, returns True
               otherwise False.
    """
    if predicate.mimetype:
        v_1 = _deep_access_(data, MIMETYPE)
        print(v_1, predicate, v_1 == predicate.mimetype)
        return v_1 == predicate.mimetype
    if predicate.url_fragment:
        value = _deep_access_(data, URL)
        if value:
            return predicate.url_fragment in value
    return False


def extract(data: Dict[str, Any], predicate: Predicate) -> List[Dict[str, Any]]:
    """accessess the HARs log entries and extracts all matching records"""
    entries = _deep_access_(data, ENTRIES)
    if not entries:
        raise ValueError(
            "File does not have values at `.logs.entries`. Is it a valied HAR-file? "
        )
    return [_ for _ in entries if match(_, predicate)]
