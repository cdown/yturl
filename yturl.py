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
import logging
from collections import namedtuple


class YturlError(Exception): error_code = None
class UnknownQualityError(YturlError): error_code = 1
class YouTubeAPIError(YturlError): error_code = 2
class NoLocallyKnownItagsAvailableError(YturlError): error_code = 3
class VideoIDParserError(YturlError): error_code = 4

log = logging.getLogger(__name__)

Itag = namedtuple('Itag', [
    'v_dimensions', 'v_bitrate', 'a_bitrate', 'a_samplerate', 'v_encoding'
])
ITAGS = {
    5:   Itag(400 * 240,   0.25, 64,  22.05, 'h263'),
    6:   Itag(480 * 270,   0.8,  64,  22.05, 'h263'),
    13:  Itag(176 * 144,   0.5,  64,  22.05, 'mp4v'),
    17:  Itag(176 * 144,   2,    64,  22.05, 'mp4v'),
    18:  Itag(640 * 360,   0.5,  96,  44.1,  'h264'),
    22:  Itag(1280 * 720,  2.9,  192, 44.1,  'h264'),
    34:  Itag(640 * 360,   0.5,  128, 44.1,  'h264'),
    35:  Itag(854 * 480,   1,    128, 44.1,  'h264'),
    36:  Itag(320 * 240,   0.17, 38,  44.1,  'mp4v'),
    37:  Itag(1920 * 1080, 2.9,  192, 44.1,  'h264'),
    38:  Itag(4096 * 3072, 5,    192, 44.1,  'h264'),
    43:  Itag(640 * 360,   0.5,  128, 44.1,  'vp8'),
    44:  Itag(854 * 480,   1,    128, 44.1,  'vp8'),
    45:  Itag(1280 * 720,  2,    192, 44.1,  'vp8'),
    46:  Itag(1920 * 1080, 2,    192, 44.1,  'vp8'),
}
ITAGS_BY_QUALITY = sorted(ITAGS, reverse=True, key=lambda itag: ITAGS[itag])

NAMED_QUALITY_GROUPS = {
    "low": -1,
    "medium": len(ITAGS_BY_QUALITY) // 2,
    "high": 0,
}

VIDEO_ID_LEN = 11
GVI_BASE_URL = 'https://www.youtube.com/get_video_info?hl=en&video_id='
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
    log.debug('Got URL params from "%s": %r', url, url_params)
    video_id = url_params.get('v', parsed_url.path.split('/')[-1])
    log.debug('Parsed video ID: "%s"', video_id)

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
    log.debug('Parsed index "%s" from input "%s"', desired_index, desired_itag)
    pairs_by_distance = list(zip_longest(
        ITAGS_BY_QUALITY[desired_index::-1],
        ITAGS_BY_QUALITY[desired_index + 1:],
    ))
    log.debug('Got itags pairs by distance: %r', pairs_by_distance)
    similar_itags = [x for x in chain(*pairs_by_distance) if x is not None]
    log.debug('Got itags by similarity: %r', similar_itags)
    return similar_itags


def itags_for_video(video_id):
    '''
    Return the available itags for a video with their associated URLs.
    '''

    log.debug('Getting available itags for video ID "%s"', video_id)
    gvi_url = GVI_BASE_URL + video_id
    api_response_raw = requests.get(gvi_url).text
    log.debug('Raw API response: %s', api_response_raw)
    api_response = dict(parse_qsl(api_response_raw))
    log.debug('Parsed API response: %r', api_response)

    try:
        streams = api_response['url_encoded_fmt_stream_map'].split(',')
    except KeyError:
        raise YouTubeAPIError(api_response.get('reason', GENERIC_API_FAIL_MSG))

    log.debug('Streams: %r', streams)
    videos = [dict(parse_qsl(stream)) for stream in streams]

    itag_and_url_pairs = [
        (int(video["itag"]), video["url"]) for video in videos
    ]
    log.debug('Itag/URL pairs: %r', itag_and_url_pairs)
    return itag_and_url_pairs


def itag_from_quality(group):
    '''
    Return the itag representing a quality group name, or if the quality is a
    known itag, return that itag.
    '''

    try:
        itag = ITAGS_BY_QUALITY[NAMED_QUALITY_GROUPS[group]]
    except KeyError:
        if group in ITAGS_BY_QUALITY:
            # This is actually an itag, not a group.
            itag = group
        else:
            raise UnknownQualityError(
                '{group!r} is not a known quality (known: {known})'.format(
                    group=group, known=', '.join(NAMED_QUALITY_GROUPS),
                )
            )

    log.debug('Parsed itag "%s" from group "%s"', itag, group)
    return itag


def most_similar_available_itag(desired_itag, available_itags):
    '''
    Return the most similar available itag to the desired itag. See
    itags_by_similarity for information about how "similarity" is determined.
    '''

    itags_by_preference = itags_by_similarity(desired_itag)

    for itag in itags_by_preference:
        if itag in available_itags:
            log.debug('First preferred itag available is "%s"', itag)
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
    parser.add_argument(
        '--debug',
        action='store_const', dest='log_level',
        const=logging.DEBUG, default=logging.WARNING,
        help='enable debug logging',
    )
    return parser.parse_args(args)


def run(argv=None, force_return=False):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_args(argv)
    logging.basicConfig(level=args.log_level)

    video_id = video_id_from_url(args.url)
    desired_itag = itag_from_quality(args.quality)
    video_itags = dict(itags_for_video(video_id))

    most_similar_itag = most_similar_available_itag(desired_itag, video_itags)
    url_to_video = video_itags[most_similar_itag]

    print('Using itag {0}.'.format(most_similar_itag), file=sys.stderr)
    print(url_to_video)

    if force_return:
        return url_to_video


def main():
    try:
        run()
    except YturlError as thrown_exc:
        print('fatal: {0!s}'.format(thrown_exc), file=sys.stderr)
        sys.exit(thrown_exc.error_code)


if __name__ == '__main__':
    main()
