#!/usr/bin/env python2

import os
import yturl
from nose.tools import assert_raises, eq_ as eq
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
    with open(os.path.join(SCRIPT_DIR, 'files/success_input')) as success_f:
        urlopen_mock.read.return_value = success_f.read()

    avail = yturl.itags_for_video("fake")
    eq(list(avail),
        [(43,
	  'http://r1---sn-uh-30as.googlevideo.com/videoplayback?itag=43&' +
          'ratebypass=yes&fexp=935640%2C943900%2C932261%2C945508%2C937417%2C' +
          '913434%2C936910%2C936913%2C902907%2C934022&upn=7S8Or-4r_ts&key=yt' +
          '5&ip=175.143.73.193&signature=4674C661CDD8B4A7D75537DC360B30FE9A0' +
          '156C7.07375770BEA4BCC1BA7F99D1775D9DC5DD794CF0&mt=1394594747&expi' +
          're=1394617426&id=2b16823874f4a662&sver=3&ms=au&ipbits=0&mv=m&spar' +
          'ams=id%2Cip%2Cipbits%2Citag%2Cratebypass%2Csource%2Cupn%2Cexpire&' +
          'source=youtube'),
         (18,
          'http://r1---sn-uh-30as.googlevideo.com/videoplayback?i' +
          'tag=18&ratebypass=yes&fexp=935640%2C943900%2C932261%2C945508%2C93' +
          '7417%2C913434%2C936910%2C936913%2C902907%2C934022&upn=7S8Or-4r_ts' +
          '&key=yt5&ip=175.143.73.193&signature=46EB2808DCE945183ACF0EF8A6C4' +
          '073AC3F4C6E4.A2157CC9734898D5C70379152F9FD20B7DF9A8BE&mt=13945947' +
          '47&expire=1394617426&id=2b16823874f4a662&sver=3&ms=au&ipbits=0&mv' +
          '=m&sparams=id%2Cip%2Cipbits%2Citag%2Cratebypass%2Csource%2Cupn%2C' +
          'expire&source=youtube'),
         (5,
          'http://r1---sn-uh-30as.googlevideo.com/videoplayback?i' +
          'tag=5&fexp=935640%2C943900%2C932261%2C945508%2C937417%2C913434%2C' +
          '936910%2C936913%2C902907%2C934022&ipbits=0&upn=7S8Or-4r_ts&factor' +
          '=1.25&algorithm=throttle-factor&ip=175.143.73.193&key=yt5&mt=1394' +
          '594747&expire=1394617426&id=2b16823874f4a662&sver=3&sparams=algor' +
          'ithm%2Cburst%2Cfactor%2Cid%2Cip%2Cipbits%2Citag%2Csource%2Cupn%2C' +
          'expire&ms=au&source=youtube&mv=m&signature=A8CA3254FD670B0C2DFE3A' +
          'F49741A287B63FCB40.3BC7D9A5E6CAFE0D95B1139BB6140DB9D3ED3C67&burst' +
          '=40'),
         (36,
          'http://r1---sn-uh-30as.googlevideo.com/videoplayback?i' +
          'tag=36&fexp=935640%2C943900%2C932261%2C945508%2C937417%2C913434%2' +
          'C936910%2C936913%2C902907%2C934022&ipbits=0&upn=7S8Or-4r_ts&facto' +
          'r=1.25&algorithm=throttle-factor&ip=175.143.73.193&key=yt5&mt=139' +
          '4594747&expire=1394617426&id=2b16823874f4a662&sver=3&sparams=algo' +
          'rithm%2Cburst%2Cfactor%2Cid%2Cip%2Cipbits%2Citag%2Csource%2Cupn%2' +
          'Cexpire&ms=au&source=youtube&mv=m&signature=0D85E1CBEC334944C7A1E' +
          'EFDEA68443797E6840E.67CB67ECDC3897D85DCD6E916018620CE77A6D74&burs' +
          't=40'),
         (17,
          'http://r1---sn-uh-30as.googlevideo.com/videoplayback?i' +
          'tag=17&fexp=935640%2C943900%2C932261%2C945508%2C937417%2C913434%2' +
          'C936910%2C936913%2C902907%2C934022&ipbits=0&upn=7S8Or-4r_ts&facto' +
          'r=1.25&algorithm=throttle-factor&ip=175.143.73.193&key=yt5&mt=139' +
          '4594747&expire=1394617426&id=2b16823874f4a662&sver=3&sparams=algo' +
          'rithm%2Cburst%2Cfactor%2Cid%2Cip%2Cipbits%2Citag%2Csource%2Cupn%2' +
          'Cexpire&ms=au&source=youtube&mv=m&signature=6346FE1E173305971800C' +
          '7C83AB4B91C85065FBA.E167ACFB63BCE0A20157527AFF21831DB1D28CE2&burs' +
          't=40')]
    )


def test_quality_group_parsing():
    eq(yturl.itag_from_quality(18), 18)
    eq(yturl.ITAGS_BY_QUALITY.index(yturl.itag_from_quality("high")), 0)
    eq(
        yturl.ITAGS_BY_QUALITY.index(yturl.itag_from_quality("medium")),
        len(yturl.ITAGS_BY_QUALITY) // 2,
    )
    eq(
        yturl.ITAGS_BY_QUALITY.index(yturl.itag_from_quality("low")),
        len(yturl.ITAGS_BY_QUALITY) - 1,
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
