|travis| |appveyor| |lgtm| |coveralls| |libraries|

.. |travis| image:: https://img.shields.io/travis/cdown/yturl/develop.svg?label=linux%20%2B%20mac%20tests
  :target: https://travis-ci.org/cdown/yturl
  :alt: Linux and Mac tests

.. |appveyor| image:: https://img.shields.io/appveyor/ci/cdown/yturl/develop.svg?label=windows%20tests
  :target: https://ci.appveyor.com/project/cdown/yturl
  :alt: Windows tests

.. |lgtm| image:: https://img.shields.io/lgtm/grade/python/github/cdown/yturl.svg?label=code%20quality
  :target: https://lgtm.com/projects/g/cdown/yturl/overview/
  :alt: LGTM

.. |coveralls| image:: https://img.shields.io/coveralls/cdown/yturl/develop.svg?label=test%20coverage
  :target: https://coveralls.io/github/cdown/yturl?branch=develop
  :alt: Coverage

.. |libraries| image:: https://img.shields.io/librariesio/github/cdown/yturl.svg?label=dependencies
  :target: https://libraries.io/github/cdown/yturl
  :alt: Dependencies

yturl gets direct media URLs to YouTube media, freeing you having to
view them in your browser.

yturl is still maintained, but is pretty much "done". Outside of changes to
match YouTube API changes, bug fixes, and support for newer Python versions,
development is complete.

Usage
-----

By default, yturl prints the media URL to standard output.

::

    $ yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ'
    Using itag 43.
    http://r2---sn-uphxqvujvh-30al.googlevideo.com/videoplayback?source=[...]


You can use this URL in the media player of your choice. For media players that
can be launched from the command line, this typically means that you can do
something like the following to watch it in your preferred player:

::

    $ <your-preferred-player> "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"

There is also a ``-q`` option for controlling the quality (for example ``-q
high``), see :code:`yturl --help` for more information.

Installation
------------

To install the latest stable version from PyPi:

.. code::

    $ pip install -U yturl

To install the latest development version directly from GitHub:

.. code::

    $ pip install -U git+https://github.com/cdown/yturl.git@develop

Testing
-------

.. code::

    $ pip install tox
    $ tox
    ..........
    ----------------------------------------------------------------------
    Ran 10 tests in 4.088s
    OK
