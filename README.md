`yturl` gets direct media URLs to YouTube media.

# Basic syntax

    yturl [-q QUALITY] videoID/URL

# Examples

Watch a video of Bill Gates jumping over a chair in the highest quality
possible (you may also want to look at mplayer's `-cache` option):

    mplayer "$(yturl 'http://www.youtube.com/watch?v=KxaCOHT0pmI')"

Download the same video, at the closest possible quality to itag 38:

    curl -o bill "$(yturl -q 38 'http://www.youtube.com/watch?v=KxaCOHT0pmI')"

Download the same video, using the first low quality format we find:

    curl -o bill "$(yturl -q low 'http://www.youtube.com/watch?v=KxaCOHT0pmI')"

# Making life easier

If you find yourself frequently watching videos in mplayer using yturl, you can
quite easily write a shell wrapper:

    yt() {
        mplayer "$(yturl "$@")"
    }

Then just use it in the same way you would use `yturl`, calling it with `yt`.
