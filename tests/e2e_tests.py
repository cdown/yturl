#!/usr/bin/env python2

import json
import httpretty
import os
import yturl
from nose.tools import assert_raises, eq_ as eq
from mock import patch


SCRIPT_DIR = os.path.dirname(__file__)
VIDEO_ID = 'x' * 11
FAKE_URL = 'http://foo.com/' + VIDEO_ID


@httpretty.activate
@patch("yturl.urlopen")
def test_quality_as_word_ok(urlopen_mock):
    with open(os.path.join(SCRIPT_DIR, 'files/success_output')) as output_f:
        expected = dict(json.load(output_f))[43]

    with open(os.path.join(SCRIPT_DIR, 'files/success_input'), 'rb') as mock_f:
        fake_api_output = mock_f.read()

    httpretty.register_uri(
        httpretty.GET, yturl.GVI_BASE_URL + VIDEO_ID,
        body=fake_api_output, content_type='application/x-www-form-urlencoded',
    )

    chosen_uri = yturl.main(['-q', 'high', FAKE_URL], force_return=True)
    eq(chosen_uri, expected)


def test_unknown_quality():
    with assert_raises(yturl.UnknownQualityError):
        yturl.main(['-q', '123456', FAKE_URL], force_return=True)


@httpretty.activate
@patch('yturl.urlopen')
def test_youtube_api_error_exit(urlopen_mock):
    mock_filename = os.path.join(SCRIPT_DIR, 'files/embed_restricted')
    with open(mock_filename, 'rb') as mock_f:
        fake_api_output = mock_f.read()

    httpretty.register_uri(
        httpretty.GET, yturl.GVI_BASE_URL + VIDEO_ID,
        body=fake_api_output, content_type='application/x-www-form-urlencoded',
    )

    with assert_raises(yturl.YouTubeAPIError):
        yturl.main([FAKE_URL], force_return=True)
