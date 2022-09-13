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
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from loguru import logger as log

ENTRIES = ["log", "entries"]
MIMETYPE = ["response", "content", "mimeType"]
URL = ["request", "url"]

Processor = Callable[["Predicate"], Generator]
Accessor = Callable[[Dict[str, Any]], str]


def _deep_access_(
    data: Dict[str, Any], path: List[Union[str, Accessor]]
) -> Optional[Any]:
    def _reducer_(carry: Optional[Dict[str, Any]], key: Union[str, Accessor]):
        _key_ = None
        if isinstance(carry, dict):
            if isinstance(key, str):
                _key_ = key
            else:
                _key_ = key(carry)
            return carry.get(_key_)
        if isinstance(carry, list):
            if isinstance(key, str):
                _key_ = key
            else:
                _key_ = key(carry)
            return carry[_key_]
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


class WritableType:  # pylint: disable=R0903
    """discerns writable handlers"""

    binary = "BINARY"
    stream = "STREAM"
    single = "SINGLE"


@dataclasses.dataclass
class Writable:
    """Emissions of a processor function"""

    type: str
    content: Any

    def __repr__(self) -> str:
        return f"<Writable {self.type} {str(self.content)[:20]}>"


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
        log.trace(f"{v_1}, {predicate}, {v_1 == predicate.mimetype}")
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


def pluck(data: Dict[Any, Any], spec: Dict[str, List[Union[str, Accessor]]]):
    """pluck data from a dict usign a mapping of new keys to paths"""
    return {key: _deep_access_(data, path) for key, path in spec.items()}
