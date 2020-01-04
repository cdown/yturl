import collections
import os

import yturl

import httpretty
import pytest
from hypothesis import assume, given, HealthCheck, settings
from hypothesis.strategies import (
    binary,
    booleans,
    integers,
    just,
    lists,
    none,
    one_of,
    sampled_from,
)
from urllib.parse import urlencode
from tests import _test_utils

SUPPRESSED_CHECKS = [HealthCheck.too_slow]

settings.register_profile("base", settings(suppress_health_check=SUPPRESSED_CHECKS))
settings.register_profile(
    "release", settings(max_examples=1000, suppress_health_check=SUPPRESSED_CHECKS)
)
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "base"))


@given(_test_utils.video_ids(), sampled_from(_test_utils.YOUTUBE_URL_EXAMPLES))
def test_video_id_parsed_from_url(video_id, url_format):
    """
    That that video IDs are successfully parsed from URLs.
    """
    url = url_format % video_id
    assert yturl.video_id_from_url(url) == video_id


@httpretty.activate
@given(lists(integers(), min_size=1, unique_by=lambda x: x), booleans())
def test_available_itags_parsing(input_itags, is_livestream):
    """
    Test that the itag -> url map is successfully parsed from an API response.
    """
    # The YouTube get_video_info API provides its output as a urlencoded
    # string. Individual keys and values inside a urlencoded string are always
    # strings.
    #
    # As such, if we didn't convert these to strings, we'd still get strings
    # back from parse_qsl (which is called inside yturl.itags_for_video). This
    # means that the return value of itags_for_video is always a string to
    # string OrderedDict, so we must convert to strings to be able to do the
    # final equality test.
    input_itags = list(map(str, input_itags))

    # In real life, the URL will obviously not be the itag as a string, but the
    # actual URL we retrieve is inconsequential to this test. We just want to
    # check that they are parsed and linked together properly as tuples.
    itag_to_url_map = collections.OrderedDict((itag, itag) for itag in input_itags)

    # This is missing a lot of "real" keys that are returned by the YouTube API
    # inside url_encoded_fmt_stream_map, but we don't check those keys inside
    # itags_for_video, so we don't need them here.
    api_itag_map = ",".join(
        [
            urlencode({"itag": itag, "url": itag_to_url_map[itag]})
            for itag in input_itags
        ]
    )

    # This is also missing a lot of keys which are, in reality, returned by the
    # YouTube API. If key references are added inside itags_for_video, the
    # relevant keys will need to be added here.
    fake_api_output = {"url_encoded_fmt_stream_map": api_itag_map, "status": "ok"}

    if is_livestream:
        del fake_api_output["url_encoded_fmt_stream_map"]
        fake_api_output["livestream"] = "1"

    _test_utils.mock_get_video_info_api_response(urlencode(fake_api_output))

    if is_livestream:
        with pytest.raises(NotImplementedError):
            got_itags_for_video = yturl.itags_for_video(_test_utils.VIDEO_ID)
    else:
        got_itags_for_video = yturl.itags_for_video(_test_utils.VIDEO_ID)

        # dict to OrderedDict comparisons don't care about order, so if we
        # accidentally started returning a dict from itags_for_video, it's going to
        # return True even though the order actually isn't respected. As such, we
        # need to make sure the return type of itags_for_video is OrderedDict.
        assert isinstance(got_itags_for_video, collections.OrderedDict)
        assert got_itags_for_video == itag_to_url_map


@httpretty.activate
def test_status_ok_still_raises():
    """
    Test that we reraise properly if url_encoded_fmt_stream_map is missing.
    """
    fake_api_output = {"status": "ok"}
    _test_utils.mock_get_video_info_api_response(urlencode(fake_api_output))
    with pytest.raises(KeyError):
        yturl.itags_for_video(_test_utils.VIDEO_ID)


@given(integers())
def test_itag_from_quality_itag_pass_through(itag):
    """
    Test that, when passed to itag_from_quality, itags are returned unaffected.
    """
    assert yturl.itag_from_quality(itag, [itag]) == itag


@given(lists(integers(), min_size=1, unique=True))
def test_itag_from_quality_ordering(itags):
    """
    Test that quality ordering is correct from a relative index perspective.
    """

    def get_index(quality_group):
        return itags.index(yturl.itag_from_quality(quality_group, itags))

    assert get_index("high") <= get_index("medium") <= get_index("low")


@given(integers(), lists(integers()))
def test_itag_from_quality_num_but_not_available(itag, video_itags):
    """
    Test that we raise ValueError if explicitly requesting an unavailable itag.
    """
    assume(itag not in video_itags)
    with pytest.raises(ValueError):
        yturl.itag_from_quality(itag, video_itags)


@httpretty.activate
@given(one_of(binary(), none(), just("CAPTCHA")))
def test_api_error_raises(reason):
    """
    Test that we raise YouTubeAPIError when the API status is "fail".

    "reason" can be None, in which case we don't pass it in the API output. In
    this case, we should fall back to our default API error message.
    """
    api_output_dict = {"status": "fail"}

    if reason is not None:
        api_output_dict["reason"] = reason

    fake_api_output = urlencode(api_output_dict)

    _test_utils.mock_get_video_info_api_response(fake_api_output)

    with pytest.raises(yturl.YouTubeAPIError):
        yturl.itags_for_video(_test_utils.VIDEO_ID)


@given(lists(binary(min_size=1), min_size=1))
def test_parse_qs_single_duplicate_keys_raise(keys):
    """
    Test that parse_qs_single raises ValueError on encountering duplicate keys.
    """
    duplicated_keys = keys + keys
    query_string = urlencode([(key, key) for key in duplicated_keys], doseq=True)

    with pytest.raises(ValueError):
        yturl.parse_qs_single(query_string)
