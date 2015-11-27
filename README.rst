yturl gets direct media URLs to YouTube media, freeing you having to
view them in your browser.

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

    pip install -U yturl

To install the latest development version directly from GitHub:

.. code::

    pip install -U git+https://github.com/cdown/yturl.git@develop

Testing
-------

|travis| |coveralls|

.. |travis| image:: https://travis-ci.org/cdown/yturl.svg?branch=develop
  :target: https://travis-ci.org/cdown/yturl
  :alt: Test status

.. |coveralls| image:: https://coveralls.io/repos/cdown/yturl/badge.svg?branch=develop&service=github
  :target: https://coveralls.io/github/cdown/yturl?branch=develop
  :alt: Coverage

.. code::

   tox -e quick

.. _Tox: https://tox.readthedocs.org
