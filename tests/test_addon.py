"""Optionally test addons."""
import pytest


@pytest.mark.addon
def test_addon1():
    """Addon specific test"""
    pass
