"""test suite for instaxtractor.commands.reels"""

from pathlib import Path
from typing import Any, Dict

import pytest

from instaxtractor.commands.reels import reels_implementation
from instaxtractor.extract import Writable


def test_reels_implementation(har):
    """should return a Generator of Writtables"""
    for _ in reels_implementation(har):
        assert isinstance(_, Writable)


def test_reels_output(har: Dict[str, Any], tmp_path: Path):  # pylint: disable=W0613
    """should return values to write to disk"""
    pytest.skip()
