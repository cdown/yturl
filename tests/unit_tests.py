#!/usr/bin/env python2

import os
import yturl
import json
from nose.tools import assert_raises, eq_ as eq, assert_true
from mock import patch
from nose_parameterized import parameterized


SCRIPT_DIR = os.path.dirname(__file__)


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


@parameterized([
    (18, [46, 38], 46),
    (38, [17, 13], 17),
    (13, [38, 35, 17, 13], 13),
    (46, [], None),
])
def test_most_similar_available_itag(input_itag, available_itags, expected):
    itags_by_similarity = yturl.itags_by_similarity(input_itag)
    eq(
        yturl.most_similar_available_itag(
            itags_by_similarity, available_itags
        ),
        expected,
    )


@parameterized([
    ('http://www.youtube.com/watch?v=gEl6TXrkZnk&feature=pem', 'gEl6TXrkZnk'),
    ('youtu.be/gEl6TXrkZnk?feature=pem&g=q#video', 'gEl6TXrkZnk'),
    ('gEl6TXrkZnk', 'gEl6TXrkZnk'),
])
def test_video_id_from_url(url, expected):
    eq(yturl.video_id_from_url(url), expected)


@patch("yturl.urlopen")
def test_available_itags_parsing(urlopen_mock):
    with open(os.path.join(SCRIPT_DIR, 'files/success_output')) as output_f:
        expected = json.load(output_f)

    with open(os.path.join(SCRIPT_DIR, 'files/success_input'), 'rb') as temp_f:
        urlopen_mock.return_value = temp_f
        eq(list(yturl.itags_for_video('fake')), expected)


def itag_quality_pos(itag_quality):
    '''
    Return the position of an itag quality in ITAGS_BY_QUALITY, in order to
    check that index constraints hold. See test_itag_from_quality.
    '''
    return yturl.ITAGS_BY_QUALITY.index(yturl.itag_from_quality(itag_quality))


def test_itag_from_quality():
    eq(yturl.itag_from_quality(18), 18)

    # Unidentifiable values should return None
    eq(yturl.itag_from_quality(-1), None)

    assert_true(
        itag_quality_pos('high') < \
        itag_quality_pos('medium') < \
        itag_quality_pos('low')
    )


@patch("yturl.urlopen")
def test_embed_restriction_raises(urlopen_mock):
    mock_filename = os.path.join(
        os.path.dirname(__file__), "files/embed_restricted"
    )

    mock_f = open(mock_filename, "rb")
    urlopen_mock.return_value = mock_f

    avail = yturl.itags_for_video("fake")
    assert_raises(LookupError, list, avail)

    mock_f.close()
