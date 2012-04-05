`yturl` is a simple media URL grabber for YouTube.

## Usage
    yturl uri [itag ...]

## Arguments
### videoid
The video ID to get information about. This can also be a URL in a recognised
format. Any official YouTube URL (including one from alternative services like
youtu.be) should be successfully parsed, as well as many more unofficial
services (although these are not guaranteed).

### itag
The itag(s) to use. Depending on the number of itags specified, different
format selection methods may be used (see "QUALITY SELECTION").

## Quality selection
If no itags are specified on the command line, yturl will get a URL to the
highest quality format available.

If a single itag is specified on the command line, yturl will attempt to get the
URL to a video in that format, or failing that, as closely resembling that
format as is available.

If multiple itags are specified on the command line, yturl will first try to get
the URL to one of the formats specified on the command line (in order of
arguments). If none of them are available, it will then select the highest
quality video available.

Format quality order is determined by the following (where video dimensions
are the most major factor, and the video container is the least):

#### Video dimensions
The higher the video dimensions, the better the format is considered.

#### Video bitrate
The higher the video bitrate, the better the format is considered.

#### Audio sample rate
The higher the audio sample rate, the better the format is considered.

#### Audio bitrate
The higher the audio bitrate, the better the format is considered.

#### Video encoding
In order of preference: MPEG-4 AVC (H.264), Sorenson H.263, VP8, MPEG-4 Visual.

#### Video container
In order of preference: MP4, WebM, FLV, 3GP.

## Exit status
### 0
Successful operation.
### 1
Insufficient arguments.
### 2
Invalid video ID.
### 3
Invalid itag(s).
### 4
Invalid response from YouTube API.

## Bugs
Please report any bugs to https://github.com/cdown/yturl/issues.

## Copyright
Copyright 2011-2012 Christopher Down <iofc.org@christopher.down>.

This is free software; see the COPYING file for copying conditions. There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
