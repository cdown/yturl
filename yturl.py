#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import argparse
import collections
import sys

import requests

try:
    from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
except ImportError:  # Python 2 fallback
    from urllib import urlencode
    from urlparse import parse_qs, urlparse, urlunparse


# A mapping of quality names to functions that determine the desired itag from
# a list of itags. This is used when `-q quality` is passed on the command line
# to determine which available itag best suits that quality specification.
NAMED_QUALITY_GROUPS = {
    'low': lambda itags: itags[-1],
    'medium': lambda itags: itags[len(itags) // 2],
    'high': lambda itags: itags[0],
}


def construct_youtube_get_video_info_url(video_id):
    '''
    Construct a YouTube API url for the get_video_id endpoint from a video ID.
    '''
    base_parsed_api_url = urlparse('https://www.youtube.com/get_video_info')
    new_query = urlencode({'video_id': video_id})

    # As documented in the core Python docs, ._replace() is not internal, the
    # leading underscore is just to prevent name collisions with field names.
    new_parsed_api_url = base_parsed_api_url._replace(query=new_query)
    new_api_url = urlunparse(new_parsed_api_url)

    return new_api_url


def video_id_from_url(url):
    '''
    Parse a video ID, either from the "v" parameter or the last URL path slice.
    '''
    parsed_url = urlparse(url)
    url_params = parse_qs_single(parsed_url.query)
    video_id = url_params.get('v', parsed_url.path.split('/')[-1])
    return video_id


def itags_for_video(video_id):
    '''
    Return itags for a video with their media URLs, sorted by quality.
    '''
    api_url = construct_youtube_get_video_info_url(video_id)
    api_response_raw = requests.get(api_url)
    api_response = parse_qs_single(api_response_raw.text)

    if api_response.get('status') != 'ok':
        raise YouTubeAPIError(api_response.get('reason', 'Unspecified error.'))

    # The YouTube API returns these from highest to lowest quality, which we
    # rely on. From this point forward, we need to make sure we maintain order.
    streams = api_response['url_encoded_fmt_stream_map'].split(',')
    videos = [parse_qs_single(stream) for stream in streams]
    return collections.OrderedDict((vid['itag'], vid['url']) for vid in videos)


def itag_from_quality(group_or_itag, itags):
    '''
    If "group_or_itag" is a quality group, return an appropriate itag from
    itags for that group. Otherwise, group_or_itag is an itag -- just return
    it.
    '''
    if group_or_itag in NAMED_QUALITY_GROUPS:
        # "group_or_itag" is really a named quality group. Use
        # NAMED_QUALITY_GROUPS to get a function to determine the itag to use.
        func_to_get_desired_itag = NAMED_QUALITY_GROUPS[group_or_itag]
        return func_to_get_desired_itag(itags)
    elif group_or_itag in itags:
        # "group_or_itag" is really an itag. Just pass it through unaltered.
        return group_or_itag
    else:
        raise ValueError(
            'Group/itag %s unavailable (video itags: %r, known groups: %r)' % (
                group_or_itag, itags, list(NAMED_QUALITY_GROUPS),
            )
        )


def parse_qs_single(query_string):
    '''
    Parse a query string per parse_qs, but with the values as single elements.

    parse_qs, as mandated by the standard, dutifully returns each value as a
    list in case the key appears twice in the input, which can be quite
    inconvienient and results in hard to read code.

    We *could* just do dict(parse_qsl(x)), but this would indiscriminately
    discard any duplicates, and we'd rather raise an exception on that.
    Instead, we verify that no key appears twice (throwing an exception if any
    do), and then return each value as a single element in the dictionary.
    '''
    parsed_raw = parse_qs(query_string)

    for key, value in parsed_raw.items():
        if len(value) != 1:
            raise ValueError('Duplicate key: %r' % key)
        parsed_raw[key] = value[0]

    return parsed_raw


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-q', '--quality', default='medium', help='low/medium/high or an itag',
    )
    parser.add_argument(
        'video_id', metavar='video_id/url', type=video_id_from_url,
    )
    args = parser.parse_args(argv)

    itag_to_url_map = itags_for_video(args.video_id)
    desired_itag = itag_from_quality(args.quality, list(itag_to_url_map))

    print('Using itag %s.' % desired_itag, file=sys.stderr)
    print(itag_to_url_map[desired_itag])


class YouTubeAPIError(Exception):
    '''
    Raised when the YouTube API returns failure. This is not used when issues
    arise during processing of the received API data -- in those cases, we use
    more specific exception types.
    '''
    pass


if __name__ == '__main__':
    main()
