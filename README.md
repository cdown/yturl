[![Build Status](https://travis-ci.org/cdown/yturl.png?branch=master)](https://travis-ci.org/cdown/yturl)

yturl gets direct media URLs to YouTube media, allowing you to play them in
your favourite media player, download them, or do whatever you like.

# Usage

To get the media URL for a video, all you need to do is pass the URL to the
video as an argument:

    yturl youtu.be/kTFZyl7hfBw

You can get higher quality by using `-q high`.

It's up to you what you do with the URL. I usually view the video in
[mpv][mpv]:

    mpv "$(yturl youtu.be/kTFZyl7hfBw)"

You might consider using a shell function if you do this often, which allows
you to pass any yturl arguments and automatically have the video play in mpv:

    yt() { mpv "$(yturl "$@")"; }

You can replace mpv with your media player of choice.

[mpv]: http://mpv.io/
