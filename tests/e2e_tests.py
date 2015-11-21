#!/usr/bin/env python2

import json
import httpretty
import yturl
from nose.tools import assert_raises, eq_ as eq
from nose_parameterized import parameterized
from tests import _test_utils


@parameterized([
    ('high', 43),
    ('medium', 5),
    ('low', 17),
])
@httpretty.activate
def test_quality_as_word_ok(quality_word, expected_itag):
    '''
    Test that qualities are correctly parsed into their equivalent itags.

    A unit test for this is not enough, as this involves configuration of the
    argument parser, and determination of output from the program. This is
    essentially our "everything is generally ok" end to end test.
    '''
    # expected_raw is a sequence of (itag, url) pairs. Since we're specifically
    # looking for the itag corresponding to to the quality word, we convert
    # these tuples to a dict and pull out the URL for the expected itag.
    expected_raw = _test_utils.read_fixture('files/success_output')
    expected_url = dict(json.loads(expected_raw))[expected_itag]

    fake_api_output = _test_utils.read_fixture('files/success_input', 'rb')
    _test_utils.mock_get_video_info_api_response(fake_api_output)

    chosen_url = yturl.main(
        ['-q', quality_word, _test_utils.FAKE_URL],
        force_return=True,
    )

    eq(chosen_url, expected_url)


@httpretty.activate
def test_unknown_quality():
    fake_api_output = _test_utils.read_fixture('files/success_input', 'rb')
    _test_utils.mock_get_video_info_api_response(fake_api_output)

    unknown_itag = '99999999'

    with assert_raises(ValueError):
        yturl.main(
            ['-q', unknown_itag, _test_utils.FAKE_URL],
            force_return=True,
        )


@httpretty.activate
def test_youtube_api_error_exit():
    fake_api_output = _test_utils.read_fixture('files/embed_restricted')
    _test_utils.mock_get_video_info_api_response(fake_api_output)
    with assert_raises(yturl.YouTubeAPIError):
        yturl.main([_test_utils.FAKE_URL], force_return=True)
