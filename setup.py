#!/usr/bin/env python

from setuptools import setup


with open('README.rst') as readme_f:
    README = readme_f.read()

with open('requirements.txt') as requirements_f:
    REQUIREMENTS = requirements_f.readlines()

with open('tests/requirements.txt') as test_requirements_f:
    TEST_REQUIREMENTS = test_requirements_f.readlines()


setup(
    name='yturl',
    version='1.20.0',
    description='Gets direct media URLs to YouTube media',
    long_description=README,
    url='https://github.com/cdown/yturl',
    license='ISC',

    author='Chris Down',
    author_email='chris@chrisdown.name',

    py_modules=['yturl'],

    entry_points={
        'console_scripts': ['yturl=yturl:main'],
    },

    keywords='youtube media video',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Multimedia',
        'Topic :: Internet',
        'Topic :: Utilities',
    ],

    install_requires=REQUIREMENTS,

    test_suite='nose.collector',
    tests_require=TEST_REQUIREMENTS,
)
