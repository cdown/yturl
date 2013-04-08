`yturl` gets direct media URLs to YouTube media.

# Basic syntax

    yturl "video ID or a URL" [itag [itag ...]]

# Examples

Watch a video of Bill Gates jumping over a chair (you may also want to look at
mplayer's `-cache` option):

    mplayer "$(yturl 'http://www.youtube.com/watch?v=KxaCOHT0pmI')"

Download the same video, at the closest possible quality to itag 38:

    curl -o bill "$(yturl 'http://www.youtube.com/watch?v=KxaCOHT0pmI' 38)"

# Making life easier

If you find yourself frequently watching videos in mplayer using yturl, you can
quite easily write a shell wrapper:

    yt() {
        mplayer "$(yturl "$@")"
    }

Then just use it in the same way you would use `yturl`, calling it with `yt`.

# Quality selection

If no itags are specified on the command line, yturl will get a URL to the
highest quality format available.

If a single itag is specified on the command line, yturl will attempt to get
the URL to a video in that format, or failing that, as closely resembling that
format as is available.

If multiple itags are specified on the command line, yturl will first try to
get the URL to one of the formats specified on the command line (in order of
arguments). If none of them are available, it will then select the highest
quality video available.

Format quality order is determined by (in order) the maximum video dimensions,
the maximum video bitrate, the maximum audio bitrate and the maximum audio
sample rate.
