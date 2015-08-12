# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth?

import six
import vcr
import types
import pprint
import unittest
import requests
from nose.tools import *  # flake8: noqa

from settings.local import (
    URL,                # e.g. 'https://staging2.osf.io/api/v2/'
    AUTH1,              # authentication details for USER1
    AUTH2,              # authentication details for USER2
    USER1_ID,           # id of USER1
    USER2_ID,           # id of USER2
    PUBLIC_NODE_ID,     # id of a public node
    PRIVATE_NODE_ID     # id of a private node that is visible to USER1 but *not* to USER2
)
from osf_api_v2_client.session import Session
from osf_api_v2_client.utils import DotDictify


# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)

my_vcr = vcr.VCR(
    cassette_library_dir='fixtures/vcr_cassettes/test_session',
    record_mode='new_episodes',  # TODO or 'once' ?
)

class TestGetRoot(unittest.TestCase):
    """
        Ensures the root is a DotDictify object with 'meta' as an attribute (because
        the JSON object has a 'meta' dictionary).
    """

    @my_vcr.use_cassette()
    def test_get_root_auth(self):
        root = SESSION_AUTH1.get_root()
        assert_true(isinstance(root, DotDictify))
        assert_true(hasattr(root, 'meta'))

    @my_vcr.use_cassette()
    def test_get_root_not_auth(self):
        root = SESSION_NO_AUTH.get_root()
        assert_true(isinstance(root, DotDictify))
        assert_true(hasattr(root, 'meta'))
