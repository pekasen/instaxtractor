"""Process Instagram Reels data
"""
from functools import partial, reduce
from typing import Any, Dict, Generator, List

import click
import ujson
from loguru import logger as log

from instaxtractor.extract import (
    MIMEType,
    Predicate,
    Writable,
    WritableType,
    extract,
    pluck,
)

metadata_spec = {
    "id": ["id"],
    "taken_at": ["taken_at"],
    "user": ["user"],
    "caption": ["accessibility_caption"],
    "media_url": [
        "image_versions2",
        "candidates",
        lambda x: x.index(
            reduce(lambda y, z: z if z["height"] >= y["height"] else y, x)
        ),
        "url",
    ],
}


@click.command()
def reels(**kwargs):
    """collect reel data"""
    return partial(reels_implementation, **kwargs)


def reels_implementation(file: Dict[str, Any]) -> Generator[Writable, None, None]:
    """a recipe to extract reels media and data from a single HAR file"""
    # first order of business: get all JSON documents we'll need to process
    docs = extract(file, Predicate(MIMEType.JSON, "api/v1/feed/"))

    def process_media_item(url: str):
        media = extract(
            file,
            Predicate(mimetype=MIMEType.JPEG, url_fragment=url),
        )
        if media:
            try:
                image = media[0]["response"]["content"]["text"]
            except IndexError:
                log.critical("Did not find what you were looking for.")
                return
            yield Writable(WritableType.binary, image)

    def process_item(reel_items):
        for item in reel_items:
            metadata = pluck(item, metadata_spec)
            log.debug(f"Metadata parsed: {metadata}")
            yield Writable(WritableType.stream, metadata)

            if metadata["media_url"]:
                yield from process_media_item(metadata["media_url"])

    def process_users(user_reel: Dict[str, Any]):
        for payload in user_reel.values():
            reel_items = payload.get("items")
            if reel_items:
                yield from process_item(reel_items)

    def process_docs(docs: List[Dict[str, Any]]):
        for doc in docs:
            try:
                json_string = doc["response"]["content"]["text"]
                doc_data = ujson.loads(json_string)
            except ujson.JSONDecodeError:
                log.critical("Cannot parse document")
                continue
            except KeyError:
                log.warning("Empty response in {doc}")
                continue
            user_reel = doc_data.get("reels")
            if user_reel:
                yield from process_users(user_reel)

    yield from process_docs(docs)

    # for doc in docs:
    #     try:
    #         json_string = doc["response"]["content"]["text"]
    #         doc_data = ujson.loads(json_string)
    #     except ujson.JSONDecodeError:
    #         log.critical("Cannot parse document")
    #         continue
    #     # access reels from the Instagram API response
    #     _reels_ = doc_data.get("reels")
    #     if _reels_:
    #         for user_id, payload in _reels_.items():
    #             log.debug(f"Processing items for user {user_id}.")

    #             items = payload.get("items")
    #             if items:
    #                 for item in items:
    #                     metadata = pluck(item, metadata_spec)
    #                     log.debug(f"Metadata parsed: {metadata}")
    #                     yield Writable(WritableType.stream, metadata)
    #                     media_url = metadata["media_url"]
    #                     if media_url:
    #                         media = extract(
    #                             file,
    #                             Predicate(
    #                                 mimetype=MIMEType.JPEG, url_fragment=media_url
    #                             ),
    #                         )
    #                         if media:
    #                             try:
    #                                 image = media[0]["response"]["content"]["text"]
    #                             except IndexError:
    #                                 log.critical(
    #                                     "Did not find what you were looking for."
    #                                 )
    #                                 continue
    #                             yield Writable(WritableType.binary, image)
