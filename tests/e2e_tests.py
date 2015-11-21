#!/usr/bin/env python2

import json
import httpretty
import os
import yturl
from nose.tools import assert_raises, eq_ as eq
from tests import _test_utils


@httpretty.activate
def test_quality_as_word_ok():
    with open(os.path.join(_test_utils.TEST_BASE_DIR, 'files/success_output')) as output_f:
        expected = dict(json.load(output_f))[43]

    with open(os.path.join(_test_utils.TEST_BASE_DIR, 'files/success_input'), 'rb') as mock_f:
        fake_api_output = mock_f.read()

    _test_utils.mock_get_video_info_api_response(fake_api_output)

    chosen_uri = yturl.main(['-q', 'high', _test_utils.FAKE_URL], force_return=True)
    eq(chosen_uri, expected)


@httpretty.activate
def test_unknown_quality():
    with open(os.path.join(_test_utils.TEST_BASE_DIR, 'files/success_input'), 'rb') as mock_f:
        fake_api_output = mock_f.read()

    _test_utils.mock_get_video_info_api_response(fake_api_output)

    unknown_itag = '99999999'

    with assert_raises(ValueError):
        yturl.main(['-q', unknown_itag, _test_utils.FAKE_URL], force_return=True)


@httpretty.activate
def test_youtube_api_error_exit():
    mock_filename = os.path.join(_test_utils.TEST_BASE_DIR, 'files/embed_restricted')
    with open(mock_filename, 'rb') as mock_f:
        fake_api_output = mock_f.read()

    _test_utils.mock_get_video_info_api_response(fake_api_output)

    with assert_raises(yturl.YouTubeAPIError):
        yturl.main([_test_utils.FAKE_URL], force_return=True)
