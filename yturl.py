#!/usr/bin/env python

from __future__ import print_function, unicode_literals

try:
    from urllib.parse import parse_qsl, urlparse, urlencode
except ImportError:  # Python 2 fallback
    from urlparse import parse_qsl, urlparse
    from urllib import urlencode

import argparse
import sys
import requests
from collections import OrderedDict


class YouTubeAPIError(Exception): pass

GVI_BASE_URL = 'https://www.youtube.com/get_video_info?'
NAMED_QUALITY_GROUPS = {
    'low': lambda itags: itags[-1],
    'medium': lambda itags: itags[len(itags) // 2],
    'high': lambda itags: itags[0],
}


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
    api_url = GVI_BASE_URL + urlencode({'video_id': video_id})
    api_response_raw = requests.get(api_url).text
    api_response = dict(parse_qsl(api_response_raw))

    try:
        streams = api_response['url_encoded_fmt_stream_map'].split(',')
    except KeyError:
        raise YouTubeAPIError(api_response.get('reason', 'Unspecified error.'))

    videos = [dict(parse_qsl(stream)) for stream in streams]
    # The YouTube API returns this in quality order, which we rely on
    return OrderedDict((video['itag'], video['url']) for video in videos)


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


if __name__ == '__main__':
    main()
