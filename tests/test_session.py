import vcr
from nose.tools import *  # flake8: noqa

# Comment line below prevents unittest from deletion in import optimization
# noinspection PyUnresolvedReferences
import unittest

from osf_api_v2_client.settings.local import (
    URL,                # e.g. 'https://staging2.osf.io/api/v2/'
    AUTH1,              # authentication details for USER1
    AUTH2,              # authentication details for USER2
)
from osf_api_v2_client.session import Session
from osf_api_v2_client.utils import DotNotator


# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with
# PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to
# the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)


VCR_CASSETTE_PREFIX = 'fixtures/vcr_cassettes/test_session/'
VCR_RECORD_MODE = 'new_episodes'


class TestGetRoot(unittest.TestCase):
    """
    Ensures the root is a DotNotator object with 'meta' as an
    attribute (because the JSON object has a 'meta' dictionary).
    """

    get_root_vcr = vcr.VCR(
        cassette_library_dir='{}test_get_root'.format(VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @get_root_vcr.use_cassette()
    def test_get_root_auth(self):
        root = SESSION_AUTH1.get_root()
        assert_true(isinstance(root, DotNotator))
        assert_true(hasattr(root, 'meta'))

    @get_root_vcr.use_cassette()
    def test_get_root_no_auth(self):
        root = SESSION_NO_AUTH.get_root()
        assert_true(isinstance(root, DotNotator))
        assert_true(hasattr(root, 'meta'))
