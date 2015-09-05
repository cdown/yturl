#!/usr/bin/env python2

import json
import os
import yturl
from nose.tools import assert_raises, eq_ as eq
from mock import patch


SCRIPT_DIR = os.path.dirname(__file__)


@patch("yturl.urlopen")
def test_quality_as_word_ok(urlopen_mock):
    with open(os.path.join(SCRIPT_DIR, 'files/success_output')) as output_f:
        expected = dict(json.load(output_f))[43]

    with open(os.path.join(SCRIPT_DIR, 'files/success_input'), 'rb') as mock_f:
        urlopen_mock.return_value = mock_f
        chosen_uri = yturl.main(
            ['-q', 'high', 'http://foo.com'], force_return=True,
        )
        eq(chosen_uri, expected)

def test_unknown_quality():
    with assert_raises(yturl.UnknownQualityError):
        yturl.main(['-q', '123456', 'http://foo.com'], force_return=True)


@patch('yturl.urlopen')
def test_youtube_api_error_exit(urlopen_mock):
    mock_filename = os.path.join(SCRIPT_DIR, 'files/embed_restricted')
    with open(mock_filename, 'rb') as mock_f:
        urlopen_mock.return_value = mock_f
        with assert_raises(yturl.YouTubeAPIError):
            yturl.main(['http://foo.com'], force_return=True)
