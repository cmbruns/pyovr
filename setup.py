#!/bin/env python

from distutils.core import setup

_PYOVR_VERSION = "0.7.1000"

setup(
    name = "ovr",
    version = _PYOVR_VERSION,
    author = "Christopher Bruns",
    author_email = "cmbruns@rotatingpenguin.com",
    description = "Oculus Rift SDK (libOVR) bindings using ctypes",
    url = "https://github.com/cmbruns/pyovr",
    download_url = "https://github.com/cmbruns/pyovr/tarball/" + _PYOVR_VERSION,
    packages=['ovr'],
    keywords = "ovr oculus rift",
    classifiers = [],
)
