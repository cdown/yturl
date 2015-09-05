#!/usr/bin/env python

'''
Get direct media URLs to YouTube media, freeing you having to view them in your
browser.
'''

from __future__ import absolute_import, division, print_function, \
                       unicode_literals

try:
    from urllib.request import urlopen
    from urllib.parse import parse_qsl, urlparse
    from itertools import chain, zip_longest
except ImportError:  # Python 2 fallback
    from urllib import urlopen
    from urlparse import parse_qsl, urlparse
    from itertools import chain, izip_longest as zip_longest

import argparse
import sys
from collections import namedtuple


class YturlError(Exception): pass
class UnknownQualityError(YturlError): pass
class YouTubeAPIError(YturlError): pass
class NoLocallyKnownItagsAvailableError(YturlError): pass


Itag = namedtuple('Itag', [
    'v_dimensions', 'v_bitrate', 'a_bitrate', 'a_samplerate', 'v_encoding'
])


ITAGS = {
    5:   Itag(400*240,   0.25, 64,  22.05, 'h263'),
    6:   Itag(480*270,   0.8,  64,  22.05, 'h263'),
    13:  Itag(176*144,   0.5,  64,  22.05, 'mp4v'),
    17:  Itag(176*144,   2,    64,  22.05, 'mp4v'),
    18:  Itag(640*360,   0.5,  96,  44.1,  'h264'),
    22:  Itag(1280*720,  2.9,  192, 44.1,  'h264'),
    34:  Itag(640*360,   0.5,  128, 44.1,  'h264'),
    35:  Itag(854*480,   1,    128, 44.1,  'h264'),
    36:  Itag(320*240,   0.17, 38,  44.1,  'mp4v'),
    37:  Itag(1920*1080, 2.9,  192, 44.1,  'h264'),
    38:  Itag(4096*3072, 5,    192, 44.1,  'h264'),
    43:  Itag(640*360,   0.5,  128, 44.1,  'vp8'),
    44:  Itag(854*480,   1,    128, 44.1,  'vp8'),
    45:  Itag(1280*720,  2,    192, 44.1,  'vp8'),
    46:  Itag(1920*1080, 2,    192, 44.1,  'vp8'),
}
ITAGS_BY_QUALITY = sorted(ITAGS, reverse=True, key=lambda itag: ITAGS[itag])

NAMED_QUALITY_GROUPS = {
    "low": -1,
    "medium": len(ITAGS_BY_QUALITY) // 2,
    "high": 0,
}


def video_id_from_url(url):
    '''
    Parse a video ID from a YouTube URL.
    '''

    parsed_url = urlparse(url)
    url_params = dict(parse_qsl(parsed_url.query))
    return url_params.get("v", parsed_url.path.split("/")[-1])


def itags_by_similarity(desired_itag):
    '''
    Return itags ordered by the similarity to the desired one. Similarity is
    determined by seeking outwards from the index of the desired itag in the
    sorted list of known itags.
    '''

    desired_index = ITAGS_BY_QUALITY.index(desired_itag)
    pairs_by_distance = zip_longest(
        ITAGS_BY_QUALITY[desired_index::-1],
        ITAGS_BY_QUALITY[desired_index+1:],
    )
    return (x for x in chain(*pairs_by_distance) if x is not None)


def itags_for_video(video_id):
    '''
    Return the available itags for a video with their associated URLs.
    '''

    url = "http://youtube.com/get_video_info?hl=en&video_id=" + video_id
    res_handle = urlopen(url)
    res_data = dict(parse_qsl(res_handle.read().decode("utf8")))

    try:
        streams_raw = res_data["url_encoded_fmt_stream_map"]
    except KeyError:
        raise YouTubeAPIError(res_data.get('reason', 'No reason given'))

    streams = streams_raw.split(",")
    for stream in streams:
        video = dict(parse_qsl(stream))
        yield [int(video["itag"]), video["url"]]


def itag_from_quality(group):
    '''
    Return the itag representing a quality group name, or if the quality is a
    known itag, return that itag.
    '''

    try:
        return ITAGS_BY_QUALITY[NAMED_QUALITY_GROUPS[group]]
    except KeyError:
        if group in ITAGS_BY_QUALITY:
            return group
        else:
            raise UnknownQualityError('%r is not a known quality' % group)


def most_similar_available_itag(desired_itag, available_itags):
    '''
    Return the most similar available itag to the desired itag. See
    itags_by_similarity for information about how "similarity" is determined.
    '''

    itags_by_preference = itags_by_similarity(desired_itag)

    for itag in itags_by_preference:
        if itag in available_itags:
            return itag
    else:
        raise NoLocallyKnownItagsAvailableError(
            'No local itags available. (known: %r, available: %r)' % (
                sorted(itags_by_preference), sorted(available_itags),
            )
        )


def parse_args(args):
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


def main(args=sys.argv[1:], force_return=False):
    args = parse_args(args)

    video_id = video_id_from_url(args.url)
    desired_itag = itag_from_quality(args.quality)
    video_itags = dict(itags_for_video(video_id))

    most_similar_itag = most_similar_available_itag(desired_itag, video_itags)
    url_to_video = video_itags[most_similar_itag]

    if force_return:
        return url_to_video
    else:
        print("Using itag %s." % most_similar_itag, file=sys.stderr)
        print(url_to_video)
