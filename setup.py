#!/bin/env python

from setuptools import setup

setup(
    name = "pyovr",
    version = "0.7.1000",
    author = "Christopher Bruns",
    author_email = "cmbruns@rotatingpenguin.com",
    description = ("Oculus Rift SDK (libOVR) bindings using ctypes"),
    keywords = "ovr oculus rift",
    url = "https://github.com/cmbruns/pyovr",
    packages=['ovr'],
)
