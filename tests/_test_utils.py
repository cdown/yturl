'''
Utilities shared between yturl test modules.
'''


import httpretty
import os
import string
import yturl
import hypothesis.strategies as st


VIDEO_ID = 'fakefakefak'
FAKE_URL = 'http://foo.com/' + VIDEO_ID
TEST_BASE_DIR = os.path.dirname(__file__)
YOUTUBE_URL_EXAMPLES = (
    'https://www.youtube.com/watch?v=%s&feature=pem',
    'youtu.be/%s?feature=pem&g=q#video',
    '%s'  # We also allow the user to just input the video ID raw
)


def read_fixture(rel_path, mode='r'):
    '''
    Return all data in a file relative to the current script.
    '''
    path = os.path.join(TEST_BASE_DIR, rel_path)
    with open(path, mode) as fixture_f:
        return fixture_f.read()


def video_ids(length=11):
    '''
    A Hypothesis strategy to generate YouTube video IDs.
    '''
    return st.text(
        min_size=length, max_size=length,
        alphabet=string.ascii_letters + string.digits,
    )


def mock_get_video_info_api_response(body, video_id=VIDEO_ID):
    '''
    Mock out responses to get_video_id calls, returning the value in "body".
    '''
    httpretty.register_uri(
        httpretty.GET, yturl.construct_youtube_get_video_info_url(video_id),
        body=body, content_type='application/x-www-form-urlencoded',
    )
