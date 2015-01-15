[![Linux build status][travis-image]][travis-builds]
[![Windows build status][appveyor-image]][appveyor-builds]
[![Coverage][coveralls-image]][coveralls]
[![Code health][landscape-image]][landscape]
[![Dependencies][requires-image]][requires]

[travis-builds]: https://travis-ci.org/cdown/yturl
[travis-image]: https://img.shields.io/travis/cdown/yturl/master.svg?label=linux
[appveyor-builds]: https://ci.appveyor.com/project/cdown/yturl
[appveyor-image]: https://img.shields.io/appveyor/ci/cdown/yturl/master.svg?label=windows
[coveralls]: https://coveralls.io/r/cdown/yturl
[coveralls-image]: https://img.shields.io/coveralls/cdown/yturl/master.svg
[landscape]: https://landscape.io/github/cdown/yturl/master
[landscape-image]: https://landscape.io/github/cdown/yturl/master/landscape.svg
[requires]: https://requires.io/github/cdown/yturl/requirements/?branch=master
[requires-image]: https://img.shields.io/requires/github/cdown/yturl.svg?label=deps

yturl gets direct media URLs to YouTube media, freeing you having to view them
in your browser.

## Usage

### Command line

By default, yturl prints the media URL to standard output.

    $ yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ'
    Using itag 43.
    http://r2---sn-uphxqvujvh-30al.googlevideo.com/videoplayback?source=[...]

This means that you can do something like the following to watch it in [mpv][]:

    $ mpv "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"

Or something like the following to download it (using [curl][]):

    $ curl -Lo bill "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"

There is also a `-q` option for controlling the quality, see the program help
for more information.

[mpv]: http://mpv.io
[curl]: http://curl.haxx.se

### Library

```python
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
```

### Stable

    $ pip install yturl

### Master

    $ git clone git://github.com/cdown/yturl.git
    $ cd yturl
    $ python setup.py install

## Testing

    $ pip install -r tests/requirements.txt
    $ nosetests

## License

yturl is licensed under an
[ISC license](http://en.wikipedia.org/wiki/ISC_license). Full information is in
[LICENSE.md](LICENSE.md).
