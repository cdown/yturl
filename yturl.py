#!/usr/bin/env python

'''
Get direct media URLs to YouTube media, freeing you having to view them in your
browser.
'''

from __future__ import print_function

try:
    from urllib.request import urlopen                        # no lint
    from urllib.parse import parse_qsl, urlparse              # no lint
    from itertools import chain, zip_longest                  # no lint
except ImportError:  # Python 2 fallback
    from urllib import urlopen                                # no lint
    from urlparse import parse_qsl, urlparse                  # no lint
    from itertools import chain, izip_longest as zip_longest  # no lint

import argparse
import sys
from collections import namedtuple

Itag = namedtuple('Itag', [
    'v_dimensions', 'v_bitrate', 'a_bitrate', 'a_samplerate', 'v_encoding'
])


ITAGS = {
    5:   Itag(400*240,     0.25,     64,       22.05,       "h263"),
    6:   Itag(480*270,     0.8,      64,       22.05,       "h263"),
    13:  Itag(176*144,     0.5,      64,       22.05,       "mp4v"),
    17:  Itag(176*144,     2,        64,       22.05,       "mp4v"),
    18:  Itag(640*360,     0.5,      96,       44.1,        "h264"),
    22:  Itag(1280*720,    2.9,      192,      44.1,        "h264"),
    34:  Itag(640*360,     0.5,      128,      44.1,        "h264"),
    35:  Itag(854*480,     1,        128,      44.1,        "h264"),
    36:  Itag(320*240,     0.17,     38,       44.1,        "mp4v"),
    37:  Itag(1920*1080,   2.9,      192,      44.1,        "h264"),
    38:  Itag(4096*3072,   5,        192,      44.1,        "h264"),
    43:  Itag(640*360,     0.5,      128,      44.1,        "vp8"),
    44:  Itag(854*480,     1,        128,      44.1,        "vp8"),
    45:  Itag(1280*720,    2,        192,      44.1,        "vp8"),
    46:  Itag(1920*1080,   2,        192,      44.1,        "vp8"),
}
ITAGS_BY_QUALITY = sorted(ITAGS, reverse=True, key=lambda itag: ITAGS[itag])


def video_id_from_url(url):
    r'''
    Parse a video ID from a YouTube URL.

    >>> import yturl
    >>> yturl.video_id_from_url('https://www.youtube.com/watch?v=8TCxE0bWQeQ')
    '8TCxE0bWQeQ'
    >>> yturl.video_id_from_url('https://youtu.be/8TCxE0bWQeQ')
    '8TCxE0bWQeQ'

    :param url: A YouTube URL or video ID
    :type url: str
    :returns: The video ID contained in the URL or string
    :rtype: str
    '''

    parsed_url = urlparse(url)
    url_params = dict(parse_qsl(parsed_url.query))
    return url_params.get("v", parsed_url.path.split("/")[-1])


def itags_by_similarity(desired_itag):
    r'''
    Return itags ordered by the similarity to the desired one. Similarity is
    determined by seeking outwards from the index of the desired itag in the
    sorted list of known itags.

    >>> import yturl
    >>> list(yturl.itags_by_similarity(18))
    [18, 6, 34, 5, 43, 36, 35, 17, 44, 13, 45, 22, 46, 37, 38]

    :param desired_itag: The itag most desired
    :type desired_itag: int
    :returns: itags in the order of similarity to the desired one
    :rtype: :term:`generator` of ints
    '''

    desired_index = ITAGS_BY_QUALITY.index(desired_itag)
    pairs_by_distance = zip_longest(
        ITAGS_BY_QUALITY[desired_index::-1],
        ITAGS_BY_QUALITY[desired_index+1:],
    )

    return (x for x in chain(*pairs_by_distance) if x is not None)


def itags_for_video(video_id):
    r'''
    Return the available itags for a video with their associated URLs.

    :param video_id: The video ID to get itags for
    :type video_id: str
    :returns: Itags and their media URLs for this video
    :rtype: :term:`generator` of int, str pairs
    '''

    url = "http://youtube.com/get_video_info?hl=en&video_id=" + video_id
    res_handle = urlopen(url)
    res_data = dict(parse_qsl(res_handle.read().decode("utf8")))

    try:
        streams_raw = res_data["url_encoded_fmt_stream_map"]
    except KeyError:
        raise LookupError(res_data["reason"])

    streams = streams_raw.split(",")
    for stream in streams:
        video = dict(parse_qsl(stream))
        yield int(video["itag"]), video["url"]


def itag_from_quality(group):
    r'''
    Return the itag representing a quality group name, or if the quality is a
    known itag, return that itag.

    >>> import yturl
    >>> yturl.itag_from_quality('medium')
    43
    >>> yturl.itag_from_quality(35)
    35

    :param group: The name of the quality group to be parsed, or an itag
    :type group: str (group) or int (itag)
    :returns: The associated itag, or None if the group or itag is unknown
    :rtype: int or None
    '''

    groups = {
        "low": -1,
        "medium": len(ITAGS_BY_QUALITY) // 2,
        "high": 0,
    }

    try:
        return ITAGS_BY_QUALITY[groups[group]]
    except KeyError:
        if group in ITAGS_BY_QUALITY:
            return group


def most_similar_available_itag(itags_by_preference, available_itags):
    r'''
    Return the most similar available itag to the desired itag. See
    itags_by_similarity for information about how "similarity" is determined.

    >>> import yturl
    >>> yturl.most_similar_available_itag((5, 4, 3, 2, 1), (1, 4, 2))
    4

    :param itags_by_preference: A list of itags, from the most desired to least
                                desired
    :type itags_by_preference: :term:`iterator` of ints
    :param available_itags: The itags available for this video
    :type available_itags: :term:`iterator` of ints
    :returns: the most similar available itag
    :rtype: int
    '''

    for itag in itags_by_preference:
        if itag in available_itags:
            return itag


def _parse_args(args):
    '''
    Parse command line arguments.

    :param args: the command line arguments to parse
    :returns: a Namespace object representing the parsed arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q", "--quality",
        help='"low", "medium", "high", or an itag',
        default="medium",
    )
    parser.add_argument(
        "url",
        metavar="video_id/url",
        help="a YouTube url (or bare video ID)",
    )
    args = parser.parse_args(args)

    try:
        args.quality = int(args.quality)
    except ValueError:
        pass

    return args


def _main(args=sys.argv[1:], force_return=False):
    '''
    The entry point for the CLI application.

    :param args: the arguments to pass to argparse
    :param force_return: whether to return the URL for testing (not default as
                         console_scripts prints this to stderr)
    '''

    args = _parse_args(args)

    video_id = video_id_from_url(args.url)
    desired_itag = itag_from_quality(args.quality)

    if desired_itag is None:
        print("Unknown quality: %d" % args.quality, file=sys.stderr)
        sys.exit(2)

    try:
        video_itags = dict(itags_for_video(video_id))
    except LookupError as err:
        print("YouTube API error: " + str(err), file=sys.stderr)
        sys.exit(3)

    similar_itags = itags_by_similarity(desired_itag)
    most_similar_itag = most_similar_available_itag(
        similar_itags, video_itags,
    )

    if most_similar_itag:
        url_to_video = video_itags[most_similar_itag]
        print("Using itag %s." % most_similar_itag, file=sys.stderr)
        print(url_to_video)
        if force_return:
            return url_to_video
    else:
        print("No local itags available.", file=sys.stderr)
        sys.exit(1)
