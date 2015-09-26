import os
from setuptools import setup

from distutils.core import setup
from distutils.extension import Extension

import ovr.internal

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyovr",
    version = "0.7.1000",
    author = "Christopher Bruns",
    author_email = "cmbruns@rotatingpenguin.com",
    description = ("ctypes-based Python bindings for the Oculus Rift SDK (libOVR)"),
    keywords = "ovr oculus rift",
    url = "https://github.com/cmbruns/pyovr",
    packages=['ovr'],
    ],
)