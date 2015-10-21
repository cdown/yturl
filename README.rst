yturl gets direct media URLs to YouTube media, freeing you having to
view them in your browser.

Usage
-----

By default, yturl prints the media URL to standard output.

::

    $ yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ'
    Using itag 43.
    http://r2---sn-uphxqvujvh-30al.googlevideo.com/videoplayback?source=[...]

This means that you can do something like the following to watch it in
`mpv`_:

::

    $ mpv "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"

Or something like the following to download it (using `curl`_):

::

    $ curl -Lo bill "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"

There is also a ``-q`` option for controlling the quality (for example ``-q
high``), see :code:`yturl --help` for more information.

.. _mpv: http://mpv.io
.. _curl: http://curl.haxx.se

Installation
------------

To install the latest stable version from PyPi:

.. code::

    pip install -U yturl

To install the latest development version directly from GitHub:

.. code::

    pip install -U git+https://github.com/cdown/yturl.git@develop

Testing
-------

|travis| |coveralls| |scrutinizer|

.. |travis| image:: https://travis-ci.org/cdown/yturl.svg?branch=develop
  :target: https://travis-ci.org/cdown/yturl
  :alt: Test status

.. |coveralls| image:: https://coveralls.io/repos/cdown/yturl/badge.svg?branch=develop&service=github
  :target: https://coveralls.io/github/cdown/yturl?branch=develop
  :alt: Coverage

.. |scrutinizer| image:: https://img.shields.io/scrutinizer/g/cdown/yturl/develop.svg
  :target: https://scrutinizer-ci.com/g/cdown/yturl/?branch=develop
  :alt: Code quality

.. code::

   tox -e quick

.. _Tox: https://tox.readthedocs.org
