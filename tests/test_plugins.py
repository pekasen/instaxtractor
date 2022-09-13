"""Auto-generate basic tests for all registered plugins"""

import click
import click.testing
import pytest
from importlib_metadata import entry_points


@pytest.fixture(params=list(entry_points(group="instaxtractor")))
def eps(request):
    """parametrized fixture returning plug-in EntryPoints"""
    yield request.param.load()


def test_command_type(eps):  # pylint: disable=W0621
    """should be of click.Command type"""
    assert isinstance(eps, click.Command)
