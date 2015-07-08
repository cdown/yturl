#!/usr/bin/env python

from setuptools import setup

setup(
    name="yturl",
    version="1.15.5",
    description="Gets direct media URLs to YouTube media",
    long_description="""
    Gets direct media URLs to YouTube media, freeing you having to view them in
    your browser.
    """,
    url="https://github.com/cdown/yturl",
    license='ISC',

    author="Chris Down",
    author_email="chris@chrisdown.name",

    py_modules=["yturl"],

    entry_points = {
        'console_scripts': ['yturl=yturl:_main'],
    },

    keywords='youtube media video',

    classifiers=[
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
