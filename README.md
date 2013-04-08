`yturl` gets direct media URLs to YouTube media.

# Examples

Watch a video of Bill Gates jumping over a chair:

    mplayer "$(yturl 'http://www.youtube.com/watch?v=KxaCOHT0pmI')"

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
