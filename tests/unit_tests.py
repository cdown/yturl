#!/usr/bin/env python2

import yturl
import httpretty
from nose.tools import assert_raises, eq_ as eq, assert_true
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, sampled_from, text
import string

try:
    from urllib.parse import urlencode
except ImportError:  # Python 2 fallback
    from urllib import urlencode


YOUTUBE_URL_EXAMPLES = (
    'https://www.youtube.com/watch?v=%s&feature=pem',
    'youtu.be/%s?feature=pem&g=q#video',
    '%s'  # We also allow the user to just input the video ID raw
)


def video_ids(length=11):
    '''A Hypothesis strategy to generate YouTube video IDs.'''
    return text(
        min_size=length, max_size=length,
        alphabet=string.ascii_letters + string.digits,
    )


@given(video_ids(), sampled_from(YOUTUBE_URL_EXAMPLES))
def test_video_id_parsed_from_url(video_id, url_format):
    url = url_format % video_id
    eq(yturl.video_id_from_url(url), video_id)


@httpretty.activate
@given(lists(
    integers(), min_size=1, unique_by=lambda x: x,
))
def test_available_itags_parsing(input_itags):
    input_itags = list(map(str, input_itags))
    # In real life, the URL will obvious not just be the itag as a string, but
    # the actual URL we retrieve is inconsequential to this test, we just want
    # to check that they are parsed and linked together properly.
    itag_to_url_map = {itag: itag for itag in input_itags}

    # This is missing a lot of "real" keys, but we don't check them at present,
    # so we don't need them.
    api_itag_map = ','.join([
        urlencode({
            'itag': itag,
            'url': itag_to_url_map[itag],
        }) for itag in input_itags
    ])

    fake_api_output = urlencode({
        'url_encoded_fmt_stream_map': api_itag_map,
    })

    httpretty.register_uri(
        httpretty.GET, yturl.GVI_BASE_URL + 'video_id=fake',
        body=fake_api_output, content_type='application/x-www-form-urlencoded',
    )

    eq(yturl.itags_for_video('fake'), itag_to_url_map)


@given(integers())
def test_itag_from_quality_itag_pass_through(itag):
    eq(yturl.itag_from_quality(itag, [itag]), itag)


def test_itag_from_quality_ordering():
    itags = list(range(len(yturl.NAMED_QUALITY_GROUPS)))
    assert_true(
        yturl.itag_from_quality('high', itags) <
        yturl.itag_from_quality('medium', itags) <
        yturl.itag_from_quality('low', itags)
    )


@given(integers(), lists(integers()))
def test_itag_from_quality_num_but_not_available(itag, video_itags):
    assume(itag not in video_itags)
    with assert_raises(ValueError):
        yturl.itag_from_quality(itag, video_itags)


@httpretty.activate
@given(text(), integers())
def test_api_error_raises(reason, code):
    # In Python 2, urlencode bombs on some strings since it provides no way to
    # specify an encoding, so we do it manually.
    reason = reason.encode('utf-8')

    api_output_dict = {
        'status': 'fail',
        'reason': reason,
        'code': code,
    }
    fake_api_output = urlencode(api_output_dict)

    httpretty.register_uri(
        httpretty.GET, yturl.GVI_BASE_URL + 'video_id=fake',
        body=fake_api_output, content_type='application/x-www-form-urlencoded',
    )

    with assert_raises(yturl.YouTubeAPIError):
        yturl.itags_for_video('fake')
