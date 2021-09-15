import pytest


def pytest_addoption(parser):
    parser.addoption("--addon", action="store_true", help="include the addon tests")
