|Build status|

.. |Build status| image:: https://travis-ci.org/cdown/yturl.svg?branch=develop
   :target: https://travis-ci.org/cdown/yturl

yturl gets direct media URLs to YouTube media, freeing you having to
view them in your browser.

Usage
=====

Command line
------------

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

There is also a ``-q`` option for controlling the quality, see the
program help for more information.

.. _mpv: http://mpv.io
.. _curl: http://curl.haxx.se

Library
-------

.. code:: python

    >>> video_id = yturl.video_id_from_url('http://www.youtube.com/watch?v=8TCxE0bWQeQ&hl=en-US#x')
    >>> video_id
    '8TCxE0bWQeQ'
    >>>
    >>> for itag, url in yturl.itags_for_video(video_id):
    ...     print('Itag %d: %s[...]' % (itag, url[:65]))
    ...
    Itag 43: http://r20---sn-aigllnl6.googlevideo.com/videoplayback?key=yt5&up[...]
    Itag 18: http://r20---sn-aigllnl6.googlevideo.com/videoplayback?key=yt5&up[...]
    Itag 5: http://r20---sn-aigllnl6.googlevideo.com/videoplayback?key=yt5&up[...]
    Itag 36: http://r20---sn-aigllnl6.googlevideo.com/videoplayback?key=yt5&up[...]
    Itag 17: http://r20---sn-aigllnl6.googlevideo.com/videoplayback?key=yt5&up[...]


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
    $ python setup.py install

Testing
=======

::

    $ pip install -r tests/requirements.txt
    $ nosetests

License
=======

yturl is licensed under an `ISC license`_. Full information is in the
`LICENSE`_ file.

.. _ISC license: https://en.wikipedia.org/wiki/ISC_license
.. _LICENSE: LICENSE
