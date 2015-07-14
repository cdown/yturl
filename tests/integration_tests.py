#!/usr/bin/env python2

import os
import yturl
from nose.tools import assert_raises, eq_ as eq
from mock import patch

@patch("yturl.urlopen")
def test_quality_as_word_ok(urlopen_mock):
    good_f = open(os.path.join(os.path.dirname(__file__), "files/good"), "rb")
    urlopen_mock.return_value = good_f

    chosen_uri = yturl._main(['-q', 'high', 'http://foo.com'], True)
    eq(
        chosen_uri,
        'http://r1---sn-uh-30as.googlevideo.com/videoplayback?itag=43&'
        'ratebypass=yes&fexp=935640%2C943900%2C932261%2C945508%2C937417%2C'
        '913434%2C936910%2C936913%2C902907%2C934022&upn=7S8Or-4r_ts&key=yt'
        '5&ip=175.143.73.193&signature=4674C661CDD8B4A7D75537DC360B30FE9A0'
        '156C7.07375770BEA4BCC1BA7F99D1775D9DC5DD794CF0&mt=1394594747&expi'
        're=1394617426&id=2b16823874f4a662&sver=3&ms=au&ipbits=0&mv=m&spar'
        'ams=id%2Cip%2Cipbits%2Citag%2Cratebypass%2Csource%2Cupn%2Cexpire&'
        'source=youtube'
    )

    good_f.close()

def test_unknown_quality():
    with assert_raises(SystemExit) as raise_cm:
        yturl._main(['-q', '123456', 'http://foo.com'])
    eq(raise_cm.exception.code, 2)


@patch('yturl.urlopen')
def test_youtube_api_error_exit(urlopen_mock):
    mock_filename = os.path.join(
        os.path.dirname(__file__), 'files/embed_restricted'
    )

    mock_f = open(mock_filename, 'rb')
    urlopen_mock.return_value = mock_f

    with assert_raises(SystemExit) as raise_cm:
        yturl._main(['http://foo.com'])

    eq(raise_cm.exception.code, 3)
