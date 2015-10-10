#!/usr/bin/env python2

import os
import yturl
import json
import httpretty
from nose.tools import assert_raises, eq_ as eq, assert_true
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, sampled_from, text
import string

try:
    from urllib.parse import urlencode
except ImportError:  # Python 2 fallback
    from urllib import urlencode


SCRIPT_DIR = os.path.dirname(__file__)
MAX_NUM_ITAG = max(yturl.ITAGS_BY_QUALITY)
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


@given(sampled_from(yturl.ITAGS_BY_QUALITY))
def test_itags_by_similarity(input_itag):
    itags_by_similarity = yturl.itags_by_similarity(input_itag)

    itags_by_similarity_index_dist = [
        abs(itag_quality_pos(input_itag) - itag_quality_pos(similar_itag))
        for similar_itag in itags_by_similarity
    ]

    # Check that itags are ordered from closest to the desired itag to the
    # furthest.
    eq(itags_by_similarity_index_dist, sorted(itags_by_similarity_index_dist))


@given(
    sampled_from(yturl.ITAGS_BY_QUALITY),
    lists(sampled_from(yturl.ITAGS_BY_QUALITY), min_size=1),
)
def test_most_similar_available_itag(input_itag, available_itags):
    chosen = yturl.most_similar_available_itag(input_itag, available_itags)

    input_itag_idx = itag_quality_pos(input_itag)
    chosen_itag_idx = itag_quality_pos(chosen)
    ideal_distance = abs(input_itag_idx - chosen_itag_idx)

    # No other element should be closer than the one we chose, although one
    # could be *as* close.
    assert_true(not any(
        abs(input_itag_idx - itag_quality_pos(itag)) < ideal_distance
        for itag in available_itags
    ))


@given(
    sampled_from(yturl.ITAGS_BY_QUALITY),
    lists(integers(min_value=MAX_NUM_ITAG), max_size=10),
)
def test_most_similar_available_itag_none(input_itag, available_itags):
    assume(not any(x in yturl.ITAGS_BY_QUALITY for x in available_itags))
    with assert_raises(yturl.NoLocallyKnownItagsAvailableError):
        yturl.most_similar_available_itag(input_itag, available_itags)


@given(video_ids(), sampled_from(YOUTUBE_URL_EXAMPLES))
def test_video_id_parsed_from_url(video_id, url_format):
    url = url_format % video_id
    eq(yturl.video_id_from_url(url), video_id)


@given(video_ids(length=10), sampled_from(YOUTUBE_URL_EXAMPLES))
def test_video_id_from_url_unparseable(video_id, url_format):
    url = url_format % video_id
    with assert_raises(yturl.VideoIDParserError):
        yturl.video_id_from_url(url)


@httpretty.activate
def test_available_itags_parsing():
    with open(os.path.join(SCRIPT_DIR, 'files/success_output')) as output_f:
        expected_raw = json.load(output_f)
        # JSON has no tuple type, and we return tuples from itags_for_video, so
        # we need to coerce them.
        expected = map(tuple, expected_raw)

    with open(os.path.join(SCRIPT_DIR, 'files/success_input'), 'rb') as mock_f:
        fake_api_output = mock_f.read()

    httpretty.register_uri(
        httpretty.GET, yturl.GVI_BASE_URL + 'fake',
        body=fake_api_output, content_type='application/x-www-form-urlencoded',
    )

    eq(list(yturl.itags_for_video('fake')), list(expected))


def itag_quality_pos(itag_quality):
    '''
    Return the position of an itag quality in ITAGS_BY_QUALITY, in order to
    check that index constraints hold. See test_itag_from_quality.
    '''
    return yturl.ITAGS_BY_QUALITY.index(yturl.itag_from_quality(itag_quality))


@given(sampled_from(yturl.ITAGS_BY_QUALITY))
def test_itag_from_quality_itag(itag):
    eq(yturl.itag_from_quality(itag), itag)


@given(integers())
def test_itag_from_quality_num_but_not_itag(itag):
    assume(itag not in yturl.ITAGS_BY_QUALITY)
    with assert_raises(yturl.UnknownQualityError):
        yturl.itag_from_quality(itag)


def test_itag_from_quality_ordering():
    assert_true(
        itag_quality_pos('high') <
        itag_quality_pos('medium') <
        itag_quality_pos('low')
    )


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
        httpretty.GET, yturl.GVI_BASE_URL + 'fake',
        body=fake_api_output, content_type='application/x-www-form-urlencoded',
    )

    with assert_raises(yturl.YouTubeAPIError):
        yturl.itags_for_video('fake')
