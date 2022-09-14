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
METHOD = ["request", "method"]

Processor = Callable[["Predicate"], Generator]
Accessor = Callable[[Dict[str, Any]], str]


def _deep_access_(data: Dict[str, Any], path: List) -> Optional[Any]:
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
    JSON_UTF8 = "application/json; charset=utf-8"


class HTTPMethod:  # pylint: disable=R0903
    """wrapper for HTTP methods"""

    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    OPTIONS = "OPTIONS"
    DELETE = "DELETE"


@dataclasses.dataclass
class Predicate:
    """Formulates a query against the HAR data structure"""

    mimetype: Optional[str]
    url_fragment: Optional[str]
    method: Optional[str]


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
    sink: str

    def __repr__(self) -> str:
        return f"<Writable::{self.type} {str(self.content)[:20]} ->{self.sink}>"


def match(data: Dict[str, Any], predicate: Predicate) -> bool:
    """return whether given data object matches the predicate

    Params:
        data : Dict[str, Any]
            the data to process
        predicate : Predicate
            the predicate to match the data against

    Returns:
        bool : if the record is valied and matches the predicate, returns True
               otherwise False.
    """
    ret: Optional[bool] = None
    mimetype = _deep_access_(data, MIMETYPE)
    url = _deep_access_(data, URL)
    method = _deep_access_(data, METHOD)

    if predicate.mimetype is not None:
        if mimetype is None:
            return False
        ret = predicate.mimetype in mimetype
    if predicate.method is not None:
        if method is None:
            return False
        method_match = method == predicate.method
        ret = method_match and ret if ret is not None else method_match
    if predicate.url_fragment is not None:
        if url is None:
            return False
        url_match = predicate.url_fragment in url
        ret = url_match and ret if ret is not None else url_match
    log.trace(f"{ mimetype, url, method}  {predicate} -> {ret}")
    return ret or False


def extract(data: Dict[str, Any], predicate: Predicate) -> List[Dict[str, Any]]:
    """accessess the HARs log entries and extracts all matching records"""
    entries = _deep_access_(data, ENTRIES)
    if not entries:
        raise ValueError(
            "File does not have values at `.logs.entries`. Is it a valied HAR-file? "
        )
    return [_ for _ in entries if match(_, predicate)]


def pluck(data: Dict[Any, Any], spec: Dict[str, List[Union[str, Accessor]]]):
    """pluck data from a dict using a mapping of new keys to paths"""
    return {key: _deep_access_(data, path) for key, path in spec.items()}
