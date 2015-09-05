#!/usr/bin/env python2

import os
import yturl
import json
import httpretty
from nose.tools import assert_raises, eq_ as eq, assert_true
from mock import patch
from nose_parameterized import parameterized
from hypothesis import given, assume
from hypothesis.strategies import integers, lists, sampled_from


SCRIPT_DIR = os.path.dirname(__file__)
ITAGS_BY_QUALITY = yturl.ITAGS_BY_QUALITY
MAX_NUM_ITAG = max(ITAGS_BY_QUALITY)


def test_itag_order():
    eq(
        yturl.ITAGS_BY_QUALITY,
        [38, 37, 46, 22, 45, 44, 35, 43, 34, 18, 6, 5, 36, 17, 13],
    )

@parameterized([
    (18, [18, 6, 34, 5, 43, 36, 35, 17, 44, 13, 45, 22, 46, 37, 38]),
    (38, [38, 37, 46, 22, 45, 44, 35, 43, 34, 18, 6, 5, 36, 17, 13]),
    (13, [13, 17, 36, 5, 6, 18, 34, 43, 35, 44, 45, 22, 46, 37, 38]),
    (46, [46, 22, 37, 45, 38, 44, 35, 43, 34, 18, 6, 5, 36, 17, 13]),
])
def test_itags_by_similarity(input_itag, expected):
    itags_by_similarity = yturl.itags_by_similarity(input_itag)
    eq(list(itags_by_similarity), expected)


@given(
    sampled_from(ITAGS_BY_QUALITY),
    lists(sampled_from(ITAGS_BY_QUALITY), min_size=1),
)
def test_most_similar_available_itag(input_itag, available_itags):
    chosen = yturl.most_similar_available_itag(input_itag, available_itags)

    input_itag_idx = ITAGS_BY_QUALITY.index(input_itag)
    chosen_itag_idx = ITAGS_BY_QUALITY.index(chosen)
    ideal_distance = abs(input_itag_idx - chosen_itag_idx)

    # No other element should be closer than the one we chose, although one
    # could be *as* close.
    assert_true(not any(
        abs(input_itag_idx - ITAGS_BY_QUALITY.index(itag)) < ideal_distance
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


@parameterized([
    ('http://www.youtube.com/watch?v=gEl6TXrkZnk&feature=pem', 'gEl6TXrkZnk'),
    ('youtu.be/gEl6TXrkZnk?feature=pem&g=q#video', 'gEl6TXrkZnk'),
    ('gEl6TXrkZnk', 'gEl6TXrkZnk'),
])
def test_video_id_from_url(url, expected):
    eq(yturl.video_id_from_url(url), expected)


@parameterized([
    'http://www.youtube.com/watch?v=gEl6TXrkZn&feature=pem',
    'some.other.site/gEl6TXrkZn',
    'youtu.be/gEl6TXrkZn?feature=pem&g=q#video',
    'gEl6TXrkZn',
])
def test_video_id_from_url_unparseable(url):
    with assert_raises(yturl.VideoIDParserError):
        yturl.video_id_from_url(url)


@httpretty.activate
@patch("yturl.urlopen")
def test_available_itags_parsing(urlopen_mock):
    with open(os.path.join(SCRIPT_DIR, 'files/success_output')) as output_f:
        expected_raw = json.load(output_f)
        # json has no tuple tupe, and we return tuples from itags_for_video, so
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


def test_itag_from_quality_string():
    eq(yturl.itag_from_quality('high'), 38)


def test_itag_from_quality_ordering():
    assert_true(
        itag_quality_pos('high') < \
        itag_quality_pos('medium') < \
        itag_quality_pos('low')
    )


@httpretty.activate
@patch("yturl.urlopen")
def test_embed_restriction_raises(urlopen_mock):
    mock_filename = os.path.join(SCRIPT_DIR, 'files/embed_restricted')

    with open(mock_filename, 'rb') as mock_f:
        fake_api_output = mock_f.read()

    httpretty.register_uri(
        httpretty.GET, yturl.GVI_BASE_URL + 'fake',
        body=fake_api_output, content_type='application/x-www-form-urlencoded',
    )

    avail = yturl.itags_for_video('fake')
    assert_raises(yturl.YouTubeAPIError, list, avail)
