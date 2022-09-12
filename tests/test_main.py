""" Test suite for instaxtractor.main
"""

import pytest

from instaxtractor.main import cli_implementation


@pytest.mark.parametrize("name,expectation", [("World", "Hello World!")])
def test_cli(name: str, expectation: str) -> None:
    """Asserts whether greetings are correct."""
    assert cli_implementation(name) == expectation
