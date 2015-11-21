#!/usr/bin/env python

from __future__ import print_function, unicode_literals

import argparse
import collections
import requests
import sys

try:
    from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
except ImportError:  # Python 2 fallback
    from urllib import urlencode
    from urlparse import parse_qsl, urlparse, urlunparse


NAMED_QUALITY_GROUPS = {
    'low': lambda itags: itags[-1],
    'medium': lambda itags: itags[len(itags) // 2],
    'high': lambda itags: itags[0],
}


def construct_youtube_get_video_info_url(video_id):
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
    url_params = dict(parse_qsl(parsed_url.query))
    video_id = url_params.get('v', parsed_url.path.split('/')[-1])
    return video_id


def itags_for_video(video_id):
    '''
    Return itags for a video with their media URLs, sorted by quality.
    '''
    api_url = construct_youtube_get_video_info_url(video_id)
    api_response_raw = requests.get(api_url)
    api_response = dict(parse_qsl(api_response_raw.text))

    if api_response.get('status') != 'ok':
        raise YouTubeAPIError(api_response.get('reason', 'Unspecified error.'))
    streams = api_response['url_encoded_fmt_stream_map'].split(',')

    videos = [dict(parse_qsl(stream)) for stream in streams]
    # The YouTube API returns this in quality order, which we rely on
    return collections.OrderedDict((vid['itag'], vid['url']) for vid in videos)


def itag_from_quality(group, itags):
    '''
    If "group" is a quality group, return an appropriate itag from itags
    for that group. Otherwise, group is an itag -- just return it.
    '''
    if group in NAMED_QUALITY_GROUPS:
        return NAMED_QUALITY_GROUPS[group](itags)
    elif group in itags:  # group is actually an itag, not a group
        return group
    else:
        raise ValueError(
            'Quality %s unavailable (video itags: %r, known groups: %r)' % (
                group, itags, list(NAMED_QUALITY_GROUPS),
            )
        )


def main(argv=None, force_return=False):
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

    # Goes to stderr when using console_scripts, so we can't generally return
    if force_return:
        return itag_to_url_map[desired_itag]


class YouTubeAPIError(Exception):
    '''
    Raised when the YouTube API returns failure. This is not used when issues
    arise during processing of the received API data -- in those cases, we use
    more specific exception types.
    '''
    pass


if __name__ == '__main__':
    main()
