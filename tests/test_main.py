""" Test suite for instaxtractor.main
"""

import pytest
from click.testing import CliRunner

from instaxtractor.main import cli


@pytest.mark.parametrize(
    "commands,expectation",
    [("--help", 0), ("posts", 0), ("reels", 0), ("something else", 2)],
)
def test_cli(commands: str, expectation: int) -> None:
    """Asserts whether CLI is running as expected."""
    runner = CliRunner()
    assert runner.invoke(cli, commands).exit_code == expectation
