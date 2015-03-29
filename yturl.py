#!/usr/bin/env python

'''
Get direct media URLs to YouTube media, freeing you having to view them in your
browser.
'''

try:
    from urllib.request import urlopen                        # no lint
    from urllib.parse import parse_qsl, urlparse              # no lint
    from itertools import chain, zip_longest                  # no lint
except ImportError:  # Python 2 fallback
    from urllib import urlopen                                # no lint
    from urlparse import parse_qsl, urlparse                  # no lint
    from itertools import chain, izip_longest as zip_longest  # no lint

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
    """
    Parse a video ID from a YouTube URL.

    :param url: a YouTube URL or string containing a video ID
    :returns: the video ID contained in the URL or string
    """

    parsed_url = urlparse(url)
    url_params = dict(parse_qsl(parsed_url.query))
    return url_params.get("v", parsed_url.path.split("/")[-1])


def itags_by_similarity(desired_itag):
    """
    Return itags ordered by the similarity to the desired one. Similarity is
    determined by seeking outwards from the index of the desired itag in the
    sorted list of known itags.

    :param desired_itag: the itag most desired
    :returns: itags in order of similarity to the desired one
    """

    desired_index = ITAGS_BY_QUALITY.index(desired_itag)
    pairs_by_distance = zip_longest(
        ITAGS_BY_QUALITY[desired_index::-1],
        ITAGS_BY_QUALITY[desired_index+1:],
    )

    return (x for x in chain(*pairs_by_distance) if x is not None)


def itags_for_video(video_id):
    """
    Return the available itags for a video with their associated URLs.

    :param video_id: the video ID to get itags for
    :returns: tuples of itags and their media URL
    """

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
    """
    Return the itag representing a quality group name, or if the quality is a
    known itag, return that itag.

    :param name: the name of the quality group to be parsed
    :returns: the associated itag, or None if the group is unknown
    """

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
    """
    Return the most similar available itag to the desired itag. See
    itags_by_preference for information about how "similarity" is determined.

    :param itags_by_preference: a list of itags, from the most desired to least
                                desired
    :param available_itags: the itags available for this video
    :returns: the most similar available itag
    """

    for itag in itags_by_preference:
        if itag in available_itags:
            return itag
