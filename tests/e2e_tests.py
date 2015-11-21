#!/usr/bin/env python2

import json
import httpretty
import yturl
from nose.tools import assert_raises, eq_ as eq
from tests import _test_utils


@httpretty.activate
def test_quality_as_word_ok():
    # expected_raw is a sequence of (itag, url) pairs. Since we're specifically
    # looking for the itag corresponding to "high" -- 43 -- we convert these
    # tuples to a dict and pull out the URL for 43.
    expected_raw = _test_utils.read_fixture('files/success_output')
    expected_url = dict(json.loads(expected_raw))[43]

    fake_api_output = _test_utils.read_fixture('files/success_input', 'rb')
    _test_utils.mock_get_video_info_api_response(fake_api_output)

    chosen_url = yturl.main(
        ['-q', 'high', _test_utils.FAKE_URL],
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
