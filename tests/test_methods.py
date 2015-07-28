
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

pp = pprint.PrettyPrinter(indent=4)


class TestSession(unittest.TestCase):
    # NOTE: These tests are written to be relative to the localhost:8000 api server,
    # so the values for users and node_id's will change depending on whose computer runs the test.
    def setUp(self):
        # A session authenticated by the user who created the node with PRIVATE_NODE_ID
        self.session_auth1 = Session(root_url=URL, auth=AUTH1)
        # A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
        self.session_auth2 = Session(root_url=URL, auth=AUTH2)
        # A session that is not authenticated
        self.session_no_auth = Session(root_url=URL)

    # GETTING URL

    def test_url_auth(self):
        assert_equal(self.session_auth1.root_url, "http://localhost:8000/v2/")

    def test_url_not_auth(self):
        assert_equal(self.session_no_auth.root_url, "http://localhost:8000/v2/")

    # GETTING ROOT

    def test_get_root_auth(self):
        root = self.session_auth1.root_url()
        assert_equal(root.status_code, 200)

    def test_get_root_not_auth(self):
        root = self.session_no_auth.root_url()
        assert_equal(root.status_code, 200)

    # GETTING USERS

    # TODO these tests
    def test_get_authenticated_user(self):
        pass

    def test_get_user_from_diff_auth(self):
        pass

    def test_get_user_from_not_auth(self):
        pass



    # ******************************************** REQUIRES AUTH ***********************************************
    #  The following tests won't work without authentication, and safe authentication is currently not possible
    #  with the API. -- for now I am using basic_auth, but this should change after some OAuth/token things
    #  happen.
    # **********************************************************************************************************

    # CREATING NODES
    # TODO add checks into tests to make sure the title, public, etc. are correct?

    def test_create_public_node_auth(self):
        # TODO figure out how to do this.
        # TODO capture the node_id, make it PRIVATE_NODE_ID, use it for GET, DELETE tests (& PUT/POST?)
        # TODO including tests that check that non-auth'd users *can't* put/post/delete
        new_public_node = self.session_auth1.create_node(
            "Creating public node with python 1", category="", public="true"
        )
        # print(new_public_node.status_code)
        # print(new_public_node.json()[u'data'][u'public'])
        assert_true(new_public_node.json()[u'data'][u'public'])

    def test_create_private_node(self):
        # TODO capture the node_id for this, make it PRIVATE_NODE_ID, use it for GET, DELETE tests (& PUT/POST?)
        # TODO including tests that check that non-auth'd users *can't* put/post/delete/get
        new_private_node = self.session_auth1.create_node(
            "Creating private node with python 1", category=""
        )
        assert_equal(new_private_node.status_code, 201)

    def test_create_node_not_auth(self):
        # Shouldn't work, because users must be authenticated in order to create nodes.
        new_private_node = self.session_no_auth.create_node(
            "Creating node with python 1", category=""
        )
        assert_equal(new_private_node.status_code, 403)  # forbidden status code

    # EDITING NODES

    # TODO finished?
    # TODO change this to modify the public node created by test_create_public_node
    def test_edit_public_node_auth_contrib(self):
        edited_public_node = self.session_auth1.edit_node(
            PUBLIC_NODE_ID,
            title="User's New Title",
            description="User's new description",
            category=""
        )
        assert_equal(edited_public_node.status_code, 200)
        assert_equal(edited_public_node.json()[u'data'][u'title'], "Jamie's New Title")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "Jamie's new description")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "")

    # TODO finished?
    def test_edit_public_node_auth_non_contrib(self):
        edited_public_node = self.session_auth2.edit_node(
            PUBLIC_NODE_ID,
            title="User2's New Title",
            description="User2's new description",
            category=""
        )
        assert_equal(edited_public_node.status_code, 403)
        public_node = self.session_auth2.nodes(PUBLIC_NODE_ID)
        assert_equal(public_node.json()[u'data'][u'title'], "User's New Title")
        assert_equal(public_node.json()[u'data'][u'description'], "User's new description")
        assert_equal(public_node.json()[u'data'][u'description'], "")

    # TODO finished?
    def test_edit_public_node_not_auth(self):
        edited_public_node = self.session_no_auth.edit_node(
            PUBLIC_NODE_ID,
            title="Jamie's New Title",
            description="Jamie's new description",
            category=""
        )
        assert_equal(edited_public_node.status_code, 200)
        assert_equal(edited_public_node.json()[u'data'][u'title'], "Jamie's New Title")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "Jamie's new description")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "")
        edited_public_node = self.session_no_auth.edit_node(PUBLIC_NODE_ID)
        assert_equal(edited_public_node.status_code, 200)

    # TODO finish
    def test_edit_private_node_auth_contributor(self):
        # The node with PRIVATE_NODE_ID is one created by USER1, so it should be visible to USER1.
        private_node = self.session_auth1.edit_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 200)

    # TODO finish
    def test_edit_private_node_auth_non_contributor(self):
        # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
        private_node = self.session_auth2.edit_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    # TODO finish
    def test_edit_private_node_not_auth(self):
        # Unauthenticated user should not be able to view any private node.
        private_node = self.session_no_auth.edit_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    # DELETING NODES
    # TODO write tests on deleting nodes (private, public; auth, diff_auth, not_auth
    # TODO check if Reina fixed problem of deleted nodes being returned, ability to delete nodes multiple times, etc.

    # Starter, from code used in initial testing in nodes.py:
    # response = localhost_session.delete_node('x7s9m')
    # print(response.status_code)
