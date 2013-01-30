#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "yturl",
    version = "1.13",
    description = "Get direct URLs to YouTube videos.",
    author = "Chris Down",
    author_email = "chris@chrisdown.name",
    url = "http://chrisdown.name",
    scripts = ( "yturl", ),
    data_files = (
        ( "etc/yturl", (
            "configs/itags",
        )),
        ( "usr/share/man/man1", (
            "yturl.1",
        ))
    )
)
