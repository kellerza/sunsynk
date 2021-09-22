#!/usr/bin/env python
"""Sunsynk library setup."""
from pathlib import Path

from setuptools import setup

VERSION = "0.0.4"
URL = "https://github.com/kellerza/sunsynk"

desc = Path("README.md").read_text()

req = [r.strip() for r in Path("requirements.txt").read_text().splitlines()]
req = [r for r in req if r and not r.startswith("#")]

setup(
    name="sunsynk",
    version=VERSION,
    description="Library to interface Sunsynk Hybrid Inverters",
    long_description=desc,
    long_description_content_type="text/markdown",
    url=URL,
    download_url="{}/tarball/{}".format(URL, VERSION),
    author="Johann Kellerman",
    author_email="kellerza@gmail.com",
    license="MIT",
    packages=["sunsynk"],
    install_requires=req,
    zip_safe=True,
)
