import json

import yturl

import httpretty
from abduct import captured, err, out
from nose.tools import eq_ as eq
from nose_parameterized import parameterized
from tests import _test_utils


@parameterized([("high", 43), ("medium", 5), ("low", 17)])
@httpretty.activate
def test_quality_as_word_ok(quality_word, expected_itag):
    """
    Test that qualities are correctly parsed into their equivalent itags.

    A unit test for this is not enough, as this involves configuration of the
    argument parser, and determination of output from the program. This is
    essentially our "everything is generally ok" end to end test.
    """
    # expected_raw is a sequence of (itag, url) pairs. Since we're specifically
    # looking for the itag corresponding to to the quality word, we convert
    # these tuples to a dict and pull out the URL for the expected itag.
    expected_raw = _test_utils.read_fixture("files/success_output")
    expected_url = dict(json.loads(expected_raw))[expected_itag]

    fake_api_output = _test_utils.read_fixture("files/success_input", "rb")
    _test_utils.mock_get_video_info_api_response(fake_api_output)

    with captured(out(), err()) as (stdout, stderr):
        yturl.main(["-q", quality_word, _test_utils.FAKE_URL])

    eq(stderr.getvalue(), "Using itag %d.\n" % expected_itag)
    eq(stdout.getvalue(), expected_url + "\n")
