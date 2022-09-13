"""Main Module for INSTAXTRACTOR

Constants:

    log_levels : Dict[int, str] : map int to log level

"""

import sys
from pathlib import Path

import click
import importlib_metadata as imd
from loguru import logger as log

log_levels = {0: "ERROR", 1: "WARNING", 2: "INFO", 3: "DEBUG", 4: "TRACE"}


@click.group()
@click.option("--log-level", "-v", count=True)
@click.option("--log_file", "-l", type=click.File(mode="w", encoding="utf8"))
def cli(log_level, log_file: Path) -> None:
    """iNsTa-X-TrAcToR"""
    # We use this function to setup our logging
    log.remove()  # remove all default loggers
    # and set the logging level according to user input
    _log_level_ = log_levels.get(log_level) or "CRITICAL"
    _sink_ = log_file or sys.stdout  # if a log_file is specified omit logging to stdout
    log.add(_sink_, level=_log_level_)


def _register_plugins_():
    plugins = imd.entry_points().select(group="instaxtractor")
    for plugin in plugins:
        _candidate_: click.Command = plugin.load()
        if isinstance(_candidate_, click.Command):
            cli.add_command(_candidate_, plugin.name)
        else:
            print(plugin, _candidate_, type(_candidate_))
            raise ValueError(f"{plugin.name} is not a valid click.Command")


_register_plugins_()
