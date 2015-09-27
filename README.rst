yturl gets direct media URLs to YouTube media, freeing you having to
view them in your browser.

Usage
=====

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
high``), see the program help for more information.

.. _mpv: http://mpv.io
.. _curl: http://curl.haxx.se

Installation
============

Installation requires `setuptools`_.

.. _setuptools: https://pypi.python.org/pypi/setuptools

Stable version
--------------

::

    $ pip install yturl

Development version
-------------------

::

    $ git clone git://github.com/cdown/yturl.git
    $ cd yturl
    $ pip install -r requirements.txt
    $ python setup.py install

Testing
=======

.. image:: https://travis-ci.org/cdown/yturl.svg?branch=develop
  :target: https://travis-ci.org/cdown/yturl
  :alt: Test status

First, install the test requirements:

.. code::

    $ pip install -r tests/requirements.txt

Then, to test using your current Python interpreter:

.. code::

    $ nosetests

Otherwise, to test on all supported Python versions:

.. code::

    $ tox

License
=======

yturl is licensed under an `ISC license`_. Full information is in the
`LICENSE`_ file.

.. _ISC license: https://en.wikipedia.org/wiki/ISC_license
.. _LICENSE: LICENSE
