#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()


setup(
    name="py3adb",
    version="3.0.0",
    author="Matthew Geiger",
    author_email="matthew.j.geiger@gmail.com",
    description=("Simple python module to interact with Android Debug Bridge tool"),
    license="BSD",
    keywords="python android adb",
    url="https://github.com/mgeiger/py3adb",
    packages=["py3adb"],
    long_description=readme,
    classifiers=[
        "Development Status :: 2 - Alpha",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
    ],
)
