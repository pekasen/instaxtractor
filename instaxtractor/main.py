"""Main Module for INSTAXTRACTOR

Constants:

    log_levels : Dict[int, str] : map int to log level

"""

import sys
from pathlib import Path
from typing import List

import click
import importlib_metadata as imd
import ujson
from loguru import logger as log

from instaxtractor.extract import Processor

log_levels = {0: "ERROR", 1: "WARNING", 2: "INFO", 3: "DEBUG", 4: "TRACE"}


@click.group(chain=True)
@click.option(
    "--log-level", "-v", count=True, help="logging verbosity, counting up. [0]"
)
@click.option("--log_file", "-l", type=click.File(mode="w", encoding="utf8"))
@click.option("--input", "-i", help="Globbing pattern [*.har]", default="*.har")
@click.option(
    "--output",
    "-o",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="results directory [results/]",
)
def cli(
    log_level: int,
    log_file: str,
    input: str,  # pylint: disable=W0622,W0613
    output: str,  # pylint: disable=W0613
) -> None:
    """iNsTa-X-TrAcToR"""

    # We use this function to setup our logging
    log.remove()  # remove all default loggers
    # and set the logging level according to user input
    _log_level_ = log_levels.get(log_level) or "CRITICAL"
    _sink_ = log_file or sys.stdout  # if a log_file is specified omit logging to stdout
    log.add(_sink_, level=_log_level_)


@cli.result_callback()
def process_hars(
    processors: List[Processor],
    log_level,
    log_file: Path,
    input: str,  # pylint: disable=W0622
    output: str,
):
    """processor callback"""
    log.debug(
        f"""Starting instaxtractor with the following parameter:
    processors: {processors},
    logging into {log_file or 'STDOUT'} with log_level {log_level},
    input pattern: {input},
    output directory: {output}"""
    )
    files = Path().glob(input)

    for file in files:
        with file.open("r", encoding="utf8") as json_file:
            data = ujson.load(json_file)
        for processor in processors:
            if processor:
                for _ in processor(data):
                    log.debug(_)
            else:
                log.warning("Undefined processor, skipping!")


def _register_plugins_():
    plugins = imd.entry_points().select(group="instaxtractor")
    for plugin in plugins:
        _candidate_: click.Command = plugin.load()
        if isinstance(_candidate_, click.Command):
            cli.add_command(_candidate_, plugin.name)
        else:
            print(plugin, _candidate_, type(_candidate_))
            log.critical(f"{plugin.name} is not a valid click.Command")
            sys.exit(127)


_register_plugins_()
