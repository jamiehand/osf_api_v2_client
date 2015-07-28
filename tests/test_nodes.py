# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth?

import types
import unittest
from nose.tools import *  # flake8: noqa

from base.nodes import Node
from base.session import Session

from local import (
    URL,                # e.g. 'https://staging2.osf.io/api/v2/'
    AUTH1,              # authentication details for USER1
    AUTH2,              # authentication details for USER2
    USER1_ID,           # id of USER1
    USER2_ID,           # id of USER2
    PUBLIC_NODE_ID,     # id of a public node
    PRIVATE_NODE_ID     # id of a private node that is visible to USER1 but *not* to USER2
)

import pprint
pp = pprint.PrettyPrinter(indent=4)

# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)


class TestGetNodes(unittest.TestCase):

    def test_get_node_generator(self):
        node_generator = SESSION_AUTH1.get_node_generator()
        # TODO what should my assertion(s) here be?
        assert_true(isinstance(node_generator, types.GeneratorType))
        # count = 1
        # for node in node_generator:
        #     print("***************************** {} *******************************".format(count))
        #     pp.pprint(node)
        #     count += 1

    # TODO could createfakes for USER1 with some private nodes, some public nodes and make sure node_generator
    # returns more nodes when USER1 calls node_generator().

    def test_get_public_node_auth_contrib(self):
        public_node = SESSION_AUTH1.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, Node))

    def test_get_public_node_auth_non_contrib(self):
        public_node = SESSION_AUTH2.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, Node))

    def test_get_public_node_not_auth(self):
        public_node = SESSION_NO_AUTH.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, Node))

    def test_get_private_node_auth_contrib(self):
        # The node with PRIVATE_NODE_ID is one created by USER1, so it should be visible to USER1.
        private_node = SESSION_AUTH1.get_node(PRIVATE_NODE_ID)
        assert_true(isinstance(private_node, Node))

    def test_get_private_node_auth_non_contrib(self):
        # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
        with assert_raises(ValueError):
            SESSION_AUTH2.get_node(PRIVATE_NODE_ID)

    def test_get_private_node_not_auth(self):
        # Unauthenticated user should not be able to view any private node.
        with assert_raises(ValueError):
            SESSION_NO_AUTH.get_node(PRIVATE_NODE_ID)
