#!/usr/bin/env python

'''
Get direct media URLs to YouTube media, freeing you having to view them in your
browser.
'''

from __future__ import absolute_import, division, print_function, \
                       unicode_literals

try:
    from urllib.parse import parse_qsl, urlparse
    from itertools import chain, zip_longest
except ImportError:  # Python 2 fallback
    from urlparse import parse_qsl, urlparse
    from itertools import chain, izip_longest as zip_longest

import argparse
import sys
import requests
from collections import namedtuple


class YturlError(Exception): error_code = None
class UnknownQualityError(YturlError): error_code = 1
class YouTubeAPIError(YturlError): error_code = 2
class NoLocallyKnownItagsAvailableError(YturlError): error_code = 3
class VideoIDParserError(YturlError): error_code = 4


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

VIDEO_ID_LEN = 11
GVI_BASE_URL = 'https://youtube.com/get_video_info?hl=en&video_id='
GENERIC_API_FAIL_MSG = 'The YouTube API returned malformed data.'


def video_id_from_url(url):
    '''
    Parse a video ID from a YouTube URL.

    There are basically two different types of input we're trying to parse:

    - A youtube.com URL: youtube.com/watch?v=12345&foo=bar. In this case, we
      want to grab the value of the "v" key, and return that.
    - A youtu.be URL: youtu.be/12345. In this case, we grab the path component
      from urlparse and get the last path element (I don't know of any cases
      where there would be more than one element, this is mostly just an
      artifact of how the algorithm works).
    '''

    parsed_url = urlparse(url)
    url_params = dict(parse_qsl(parsed_url.query))
    video_id = url_params.get('v', parsed_url.path.split('/')[-1])

    # Google has made no commitment about this length, although it's likely to
    # stay like this. I'd usually prefer to just let the API complain about the
    # video ID down the line so that we don't duplicate its logic to determine
    # "correctness", but we have the opportunity to make the error message much
    # clearer here.
    if len(video_id) != VIDEO_ID_LEN:
        raise VideoIDParserError(
            'Could not parse video ID from {url!r} '
            '(expected len: {expected}, got: {got})'.format(
                url=url, expected=VIDEO_ID_LEN, got=len(video_id),
            )
        )

    return video_id


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

    gvi_url = GVI_BASE_URL + video_id
    api_response_raw = requests.get(gvi_url).text
    api_response = dict(parse_qsl(api_response_raw))

    try:
        streams = api_response['url_encoded_fmt_stream_map'].split(',')
    except KeyError:
        raise YouTubeAPIError(api_response.get('reason', GENERIC_API_FAIL_MSG))

    for stream in streams:
        video = dict(parse_qsl(stream))
        yield int(video["itag"]), video["url"]


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
            raise UnknownQualityError(
                '{group!r} is not a known quality (known: {known})'.format(
                    group=group, known=', '.join(NAMED_QUALITY_GROUPS),
                )
            )


def most_similar_available_itag(desired_itag, available_itags):
    '''
    Return the most similar available itag to the desired itag. See
    itags_by_similarity for information about how "similarity" is determined.
    '''

    itags_by_preference = itags_by_similarity(desired_itag)

    for itag in itags_by_preference:
        if itag in available_itags:
            return itag

    raise NoLocallyKnownItagsAvailableError(
        'No local itags available. '
        '(known: {known_itags!r}, available: {available_itags!r})'.format(
            known_itags=sorted(itags_by_preference),
            available_itags=sorted(available_itags),
        )
    )


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-q", "--quality",
        help='"low", "medium", "high", or an itag',
        # We accept either an int or string here because this could be either
        # an itag or a quality group.
        type=lambda arg: int(arg) if arg.isdigit() else arg,
        default="medium",
    )
    parser.add_argument(
        "url",
        metavar="video_id/url",
        help="a YouTube url (or bare video ID)",
    )
    return parser.parse_args(args)


def run(args=sys.argv[1:], force_return=False):
    args = parse_args(args)

    video_id = video_id_from_url(args.url)
    desired_itag = itag_from_quality(args.quality)
    video_itags = dict(itags_for_video(video_id))

    most_similar_itag = most_similar_available_itag(desired_itag, video_itags)
    url_to_video = video_itags[most_similar_itag]

    if force_return:
        return url_to_video
    else:
        print('Using itag {0}.'.format(most_similar_itag), file=sys.stderr)
        print(url_to_video)


def main():
    try:
        run()
    except YturlError as thrown_exc:
        print('fatal: {0!s}'.format(thrown_exc), file=sys.stderr)
        sys.exit(thrown_exc.error_code)


if __name__ == '__main__':
    main()
