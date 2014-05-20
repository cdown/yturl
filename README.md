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
$ curl -o bill_chair "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"
```

[curl]: http://curl.haxx.se

## Installation

    $ pip install yturl

## Testing

[![Build status][travis-image]][travis-builds]

    $ pip install -r tests/requirements.txt
    $ nosetests

[travis-builds]: https://travis-ci.org/cdown/yturl
[travis-image]: https://travis-ci.org/cdown/yturl.png?branch=master

## License

yturl is [ISC licensed][isc]. See the LICENSE file for full details.

[isc]: http://en.wikipedia.org/wiki/ISC_license
