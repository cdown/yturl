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

### Get media URL

```
$ yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ'
Using itag 43.
http://r2---sn-uphxqvujvh-30al.googlevideo.com/videoplayback?source=[...]
```

### View video in your video player

For example, with [mpv][]:

```
$ mpv "$(yturl 'http://www.youtube.com/watch?v=8TCxE0bWQeQ')"
```

[mpv]: http://mpv.io

## Installation

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
