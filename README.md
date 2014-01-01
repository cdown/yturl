[![Build status][travis-image]][travis-builds]

yturl gets direct media URLs to YouTube media, allowing you to play them in
your favourite media player, download them, or do whatever you like.

# Usage

To get the media URL for a video, pass a URL containing the video ID:

    yturl youtu.be/kTFZyl7hfBw

You can get higher quality by using `-q high`.

It's up to you what you do with the URL. I usually view the video in
[mpv][mpv]:

    mpv "$(yturl youtu.be/kTFZyl7hfBw)"

You might use a shell function if you do this often:

    yt() { mpv "$(yturl "$@")"; }

You can replace mpv with your media player of choice.

[mpv]: http://mpv.io/
[travis-builds]: https://travis-ci.org/cdown/yturl
[travis-image]: https://travis-ci.org/cdown/yturl.png?branch=master
