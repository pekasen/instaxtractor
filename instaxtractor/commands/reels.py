"""Process Instagram Reels data!"""
import re
from functools import partial
from typing import Any, Dict, Generator, List

import click
import ujson
from loguru import logger as log

from instaxtractor.extract import (
    HTTPMethod,
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
    "media_url": ["image_versions2", "candidates"],
    "video_url": [
        "video_versions",
    ],
    "has_audio": ["has_audio"],
}


@click.command()
def reels(**kwargs):
    """Collect reel data."""
    return partial(reels_implementation, **kwargs)


def reels_implementation(file: Dict[str, Any]) -> Generator[Writable, None, None]:
    """A recipe to extract reels media and data from a single HAR file."""
    # first order of business: get all JSON documents we'll need to process
    docs = extract(
        file,
        Predicate(
            mimetype=MIMEType.JSON, url_fragment="api/v1/feed/", method=HTTPMethod.GET
        ),
    )

    def process_media_item(candidates: List[Any]):
        for candidate in candidates:
            if "url" in candidate:
                url = candidate["url"]
                media_name_re = re.compile(r"(?<=\/)(\w+\.[jpegmp4]+)")
                file_name_matches = media_name_re.search(url)
                media = extract(
                    file,
                    Predicate(mimetype=None, url_fragment=url, method=HTTPMethod.GET),
                )

                log.debug(f"Found {len(media)} matches for {url}.")

                if media and file_name_matches:
                    try:
                        image = media[0]["response"]["content"]["text"]
                    except (IndexError, KeyError):
                        log.critical("Did not find what you were looking for.")
                        return
                    file_name = file_name_matches.group(1)
                    yield Writable(WritableType.binary, image, f"{file_name}")
                    break  # break the loop so we only emit the largest file we've found

    def process_item(reel_items, user_id: str):
        for item in reel_items:
            metadata = pluck(item, metadata_spec)
            log.debug(f"Metadata parsed: {metadata}")
            yield Writable(WritableType.stream, metadata, f"{user_id}.jsonl")

            if metadata["media_url"]:
                yield from process_media_item(metadata["media_url"])
            if metadata["video_url"]:
                yield from process_media_item(metadata["video_url"])

    def process_users(user_reel: Dict[str, Any]):
        for user_id, payload in user_reel.items():
            reel_items = payload.get("items")
            if reel_items:
                yield from process_item(reel_items, user_id)

    def process_docs(docs: List[Dict[str, Any]]):
        for doc in docs:
            try:
                json_string = doc["response"]["content"]["text"]
                doc_data = ujson.loads(json_string)
            except ujson.JSONDecodeError:
                log.critical("Cannot parse document")
                continue
            except KeyError:
                log.warning(f"Empty response in {doc}")
                continue
            user_reel = doc_data.get("reels")
            if user_reel:
                yield from process_users(user_reel)

    yield from process_docs(docs)
