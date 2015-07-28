# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth?

# import mock
import pprint
import unittest
import types

import requests
from nose.tools import *  # flake8: noqa

from local import (
    URL,                # e.g. 'https://staging2.osf.io/api/v2/'
    AUTH1,              # authentication details for USER1
    AUTH2,              # authentication details for USER2
    USER1_ID,           # id of USER1
    USER2_ID,           # id of USER2
    PUBLIC_NODE_ID,     # id of a public node
    PRIVATE_NODE_ID     # id of a private node that is visible to USER1 but *not* to USER2
)

from base.users import User
from base.nodes import Node
from base.session import Session
from base.utils import DotDictify

# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)


class TestGetRoot(unittest.TestCase):
    """
        Ensures the root is a DotDictify object with 'meta' as an attribute (because
        the JSON object has a 'meta' dictionary).
    """
    def test_get_root_auth(self):
        root = SESSION_AUTH1.get_root()
        assert_true(isinstance(root, DotDictify))
        assert_true(hasattr(root, 'meta'))

    def test_get_root_not_auth(self):
        root = SESSION_NO_AUTH.get_root()
        assert_true(isinstance(root, DotDictify))
        assert_true(hasattr(root, 'meta'))
