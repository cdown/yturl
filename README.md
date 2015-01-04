[![Build status][travis-image]][travis-builds]
[![Coverage][coveralls-image]][coveralls]
[![Code quality][scrutinizer-image]][scrutinizer]

[travis-builds]: https://travis-ci.org/cdown/yturl
[travis-image]: https://img.shields.io/travis/cdown/yturl/master.svg
[coveralls]: https://coveralls.io/r/cdown/yturl
[coveralls-image]: https://img.shields.io/coveralls/cdown/yturl/master.svg
[scrutinizer]: https://scrutinizer-ci.com/g/cdown/yturl/code-structure/master/hot-spots
[scrutinizer-image]: https://img.shields.io/scrutinizer/g/cdown/yturl.svg

yturl gets direct media URLs to YouTube media, freeing you having to view them
in your browser.

```
$ yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ'
Using itag 43.
http://r2---sn-uphxqvujvh-30al.googlevideo.com/videoplayback?source=[...]
```

## Examples

### View video in your video player

Using [mpv][]:

```
$ mpv "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"
```

[mpv]: http://mpv.io

### Download video

Using [curl][]:

```
$ curl -Lo bill_chair "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"
```

[curl]: http://curl.haxx.se

## Installation

    $ pip install yturl

## Testing

    $ pip install -r tests/requirements.txt
    $ nosetests

## License

yturl is [ISC licensed][isc]. See the LICENSE file for full details.

[isc]: http://en.wikipedia.org/wiki/ISC_license
