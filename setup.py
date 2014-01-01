#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "yturl",
    version = "1.15.5",
    description = "Prints direct URLs to YouTube videos.",
    url = "https://github.com/cdown/yturl",

    author = "Chris Down",
    author_email = "chris@chrisdown.name",

    scripts = [ "yturl" ],

    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Topic :: Multimedia",
        "Topic :: Internet",
        "Topic :: Utilities",
    ],
)
