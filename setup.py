#!/bin/env python

from distutils.core import setup

# Load module version from ovr/version.py
exec(open('ovr/version.py').read())

setup(
    name = "ovr",
    version = __version__,
    author = "Christopher Bruns",
    author_email = "cmbruns@rotatingpenguin.com",
    description = "Oculus Rift SDK (libOVR) bindings using ctypes",
    url = "https://github.com/cmbruns/pyovr",
    download_url = "https://github.com/cmbruns/pyovr/tarball/" + __version__,
    packages=['ovr'],
    keywords = "ovr oculus rift",
    classifiers = [],
)
