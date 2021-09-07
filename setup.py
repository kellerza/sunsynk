#!/usr/bin/env python
"""Sunsynk library setup."""
from pathlib import Path

from setuptools import setup

VERSION = "0.0.1"
URL = "https://github.com/kellerza/sunsynk"

setup(
    name="sunsynk",
    version=VERSION,
    description="Library to interface Sunsynk Hybrid Inverters",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url=URL,
    download_url="{}/tarball/{}".format(URL, VERSION),
    author="Johann Kellerman",
    author_email="kellerza@gmail.com",
    license="MIT",
    packages=["sunsynk"],
    install_requires=["aiohttp>3.3,<4", "attrs>18", "pymodbus"],
    zip_safe=True,
)
