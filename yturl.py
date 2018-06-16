#!/usr/bin/env python

"""YouTube videos on the command line."""

from __future__ import print_function, unicode_literals

import argparse
import collections
import logging
import sys

import requests

from six import iteritems, iterkeys
from six.moves.urllib.parse import parse_qs, urlencode, urlparse, urlunparse


log = logging.getLogger(__name__)

# A mapping of quality names to functions that determine the desired itag from
# a list of itags. This is used when `-q quality` is passed on the command line
# to determine which available itag best suits that quality specification.
NAMED_QUALITY_GROUPS = {
    "low": lambda itags: itags[-1],
    "medium": lambda itags: itags[len(itags) // 2],
    "high": lambda itags: itags[0],
}
DEFAULT_HEADERS = {"User-Agent": "yturl (https://github.com/cdown/yturl)"}


def construct_youtube_get_video_info_url(video_id):
    """
    Construct a YouTube API url for the get_video_id endpoint from a video ID.
    """
    base_parsed_api_url = urlparse("https://www.youtube.com/get_video_info")
    new_query = urlencode({"video_id": video_id})

    # As documented in the core Python docs, ._replace() is not internal, the
    # leading underscore is just to prevent name collisions with field names.
    new_parsed_api_url = base_parsed_api_url._replace(query=new_query)
    new_api_url = urlunparse(new_parsed_api_url)

    return new_api_url


def video_id_from_url(url):
    """
    Parse a video ID, either from the "v" parameter or the last URL path slice.
    """
    parsed_url = urlparse(url)
    url_params = parse_qs_single(parsed_url.query)
    video_id = url_params.get("v", parsed_url.path.split("/")[-1])
    log.debug("Parsed video ID %s from %s", url, video_id)
    return video_id


def itags_for_video(video_id):
    """
    Return itags for a video with their media URLs, sorted by quality.
    """
    api_url = construct_youtube_get_video_info_url(video_id)
    api_response_raw = requests.get(api_url, headers=DEFAULT_HEADERS)
    log.debug("Raw API response: %r", api_response_raw.text)
    api_response = parse_qs_single(api_response_raw.text)
    log.debug("parse_qs_single API response: %r", api_response)

    if api_response.get("status") != "ok":
        reason = api_response.get("reason", "Unspecified error.")

        # Unfortunately YouTube returns HTML in this instance, so there's no
        # reasonable way to use api_response directly.
        if "CAPTCHA" in api_response_raw.text:
            reason = "You need to solve a CAPTCHA, visit %s" % api_url
        raise YouTubeAPIError(reason)

    # The YouTube API returns these from highest to lowest quality, which we
    # rely on. From this point forward, we need to make sure we maintain order.
    streams = api_response["url_encoded_fmt_stream_map"].split(",")
    videos = [parse_qs_single(stream) for stream in streams]
    return collections.OrderedDict((vid["itag"], vid["url"]) for vid in videos)


def itag_from_quality(group_or_itag, itags):
    """
    If "group_or_itag" is a quality group, return an appropriate itag from
    itags for that group. Otherwise, group_or_itag is an itag -- just return
    it.
    """
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
            "Group/itag %s unavailable (video itags: %r, known groups: %r)"
            % (group_or_itag, itags, list(NAMED_QUALITY_GROUPS))
        )


def parse_qs_single(query_string):
    """
    Parse a query string per parse_qs, but with the values as single elements.

    parse_qs, as mandated by the standard, dutifully returns each value as a
    list in case the key appears twice in the input, which can be quite
    inconvienient and results in hard to read code.

    We *could* just do dict(parse_qsl(x)), but this would indiscriminately
    discard any duplicates, and we'd rather raise an exception on that.
    Instead, we verify that no key appears twice (throwing an exception if any
    do), and then return each value as a single element in the dictionary.
    """
    raw_pairs = parse_qs(query_string)

    dupes = [key for (key, values) in iteritems(raw_pairs) if len(values) > 1]
    if dupes:
        raise ValueError("Duplicate keys in query string: %r" % dupes)

    one_val_pairs = {key: values[0] for (key, values) in iteritems(raw_pairs)}
    return one_val_pairs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-q", "--quality", default="medium", help="low/medium/high or an itag"
    )
    parser.add_argument(
        "--debug",
        action="store_const",
        dest="log_level",
        const=logging.DEBUG,
        default=logging.WARNING,
        help="enable debug logging",
    )
    parser.add_argument("video_id", metavar="video_id/url", type=video_id_from_url)
    args = parser.parse_args(argv)
    logging.basicConfig(level=args.log_level)

    itag_to_url_map = itags_for_video(args.video_id)

    # available_itags must be indexable for use with NAMED_QUALITY_GROUPS
    available_itags = list(iterkeys(itag_to_url_map))
    desired_itag = itag_from_quality(args.quality, available_itags)

    print("Using itag %s." % desired_itag, file=sys.stderr)
    print(itag_to_url_map[desired_itag])


class YouTubeAPIError(Exception):
    """
    Raised when the YouTube API returns failure. This is not used when issues
    arise during processing of the received API data -- in those cases, we use
    more specific exception types.
    """


if __name__ == "__main__":
    main()
