# TODO should I have this?: # -*- coding: utf-8 -*-

import unittest  # TODO tests were failing without this. Why is it gray as if it's not being used?
# import mock
import pprint, requests
from nose.tools import *  # flake8: noqa
from local import (
    URL,                # e.g. 'https://staging2.osf.io/api/v2/'
    AUTH,               # authentication details for USER
    AUTH2,              # authentication details for USER2
    USER_ID,            # id of a user (doesn't have to be id of USER or USER2)
    PUBLIC_NODE_ID,     # id of a public node
    PRIVATE_NODE_ID,    # id of a private node that is visible to USER but *not* to USER2
)

from methods import Session, User #  , Node

pp = pprint.PrettyPrinter(indent=4)

class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User(USER_ID, URL, auth=None)  # TODO should I test this with different auths?

    # ATTRIBUTES

    # TODO more tests here
    def test_user_response(self):
        """
        Ensures the user detail endpoint is returned
        """
        response = self.user.response
        assert_equal(response.status_code, 200)

    def test_user_data(self):
        """
        Ensures user.data returns a dict
        """
        data = self.user.data
        assert_true(isinstance(data, dict))

    def test_user_names(self):
        """
        Ensure that the names return strings
        """
        fullname = self.user.fullname
        assert_true(isinstance(fullname, basestring))
        given_name = self.user.given_name
        assert_true(isinstance(given_name, basestring))
        middle_name = self.user.middle_name
        assert_true(isinstance(middle_name, basestring))
        family_name = self.user.family_name
        assert_true(isinstance(family_name, basestring))
        suffix = self.user.suffix
        assert_true(isinstance(suffix, basestring))

    def test_gravatar_url(self):
        """
        Ensures user.gravatar_url returns a valid url
        """
        url = self.user.gravatar_url
        res = requests.get(url)
        assert_equal(res.status_code, 200)

class TestSession(unittest.TestCase):
    # NOTE: These tests are written to be relative to the localhost:8000 api server,
    # so the values for users and node_id's will change depending on whose computer runs the test.
    def setUp(self):
        # A session authenticated by the user who created the node with PRIVATE_NODE_ID
        self.session_with_auth = Session(url=URL, auth=AUTH)
        # A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
        self.session_with_different_auth = Session(url=URL, auth=AUTH2)
        # A session that is not authenticated
        self.session_with_no_auth = Session(url=URL)

    # GETTING URL

    def test_url_auth(self):
        assert_equal(self.session_with_auth.url, "http://localhost:8000/v2/")

    def test_url_not_auth(self):
        assert_equal(self.session_with_no_auth.url, "http://localhost:8000/v2/")

    # GETTING ROOT

    def test_get_root_auth(self):
        root = self.session_with_auth.root()
        assert_equal(root.status_code, 200)

    def test_get_root_not_auth(self):
        root = self.session_with_no_auth.root()
        assert_equal(root.status_code, 200)

    # GETTING USERS

    # TODO these tests
    def test_get_authenticated_user(self):
        pass

    def test_get_user_from_diff_auth(self):
        pass

    def test_get_user_from_not_auth(self):
        pass

    # GETTING NODES

    def test_get_public_node_auth_contrib(self):
        public_node = self.session_with_auth.get_node(PUBLIC_NODE_ID)
        assert_equal(public_node.status_code, 200)

    def test_get_public_node_auth_non_contrib(self):
        public_node = self.session_with_different_auth.get_node(PUBLIC_NODE_ID)
        assert_equal(public_node.status_code, 200)

    def test_get_public_node_not_auth(self):
        public_node = self.session_with_no_auth.get_node(PUBLIC_NODE_ID)
        assert_equal(public_node.status_code, 200)

    def test_get_private_node_auth_contrib(self):
        # The node with PRIVATE_NODE_ID is one created by USER, so it should be visible to USER.
        private_node = self.session_with_auth.get_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 200)

    def test_get_private_node_auth_non_contrib(self):
        # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
        private_node = self.session_with_different_auth.get_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    def test_get_private_node_not_auth(self):
        # Unauthenticated user should not be able to view any private node.
        private_node = self.session_with_no_auth.get_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

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
        new_public_node = self.session_with_auth.create_node(
            "Creating public node with python 1", category="", public="true"
        )
        # print(new_public_node.status_code)
        # print(new_public_node.json()[u'data'][u'public'])
        assert_true(new_public_node.json()[u'data'][u'public'])

    def test_create_private_node(self):
        # TODO capture the node_id for this, make it PRIVATE_NODE_ID, use it for GET, DELETE tests (& PUT/POST?)
        # TODO including tests that check that non-auth'd users *can't* put/post/delete/get
        new_private_node = self.session_with_auth.create_node(
            "Creating private node with python 1", category=""
        )
        assert_equal(new_private_node.status_code, 201)

    def test_create_node_not_auth(self):
        # Shouldn't work, because users must be authenticated in order to create nodes.
        new_private_node = self.session_with_no_auth.create_node(
            "Creating node with python 1", category=""
        )
        assert_equal(new_private_node.status_code, 403)  # forbidden status code

    # EDITING NODES

    # TODO finished?
    # TODO change this to modify the public node created by test_create_public_node
    def test_edit_public_node_auth_contrib(self):
        edited_public_node = self.session_with_auth.edit_node(
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
        edited_public_node = self.session_with_different_auth.edit_node(
            PUBLIC_NODE_ID,
            title="User2's New Title",
            description="User2's new description",
            category=""
        )
        assert_equal(edited_public_node.status_code, 403)
        public_node = self.session_with_different_auth.get_node(PUBLIC_NODE_ID)
        assert_equal(public_node.json()[u'data'][u'title'], "User's New Title")
        assert_equal(public_node.json()[u'data'][u'description'], "User's new description")
        assert_equal(public_node.json()[u'data'][u'description'], "")

    # TODO finished?
    def test_edit_public_node_not_auth(self):
        edited_public_node = self.session_with_no_auth.edit_node(
            PUBLIC_NODE_ID,
            title="Jamie's New Title",
            description="Jamie's new description",
            category=""
        )
        assert_equal(edited_public_node.status_code, 200)
        assert_equal(edited_public_node.json()[u'data'][u'title'], "Jamie's New Title")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "Jamie's new description")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "")
        edited_public_node = self.session_with_no_auth.edit_node(PUBLIC_NODE_ID)
        assert_equal(edited_public_node.status_code, 200)

    # TODO finish
    def test_edit_private_node_auth_contributor(self):
        # The node with PRIVATE_NODE_ID is one created by USER, so it should be visible to USER.
        private_node = self.session_with_auth.edit_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 200)

    # TODO finish
    def test_edit_private_node_auth_non_contributor(self):
        # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
        private_node = self.session_with_different_auth.edit_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    # TODO finish
    def test_edit_private_node_not_auth(self):
        # Unauthenticated user should not be able to view any private node.
        private_node = self.session_with_no_auth.edit_node(PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    # DELETING NODES
    # TODO write tests on deleting nodes (private, public; auth, diff_auth, not_auth
    # TODO check if Reina fixed problem of deleted nodes being returned, ability to delete nodes multiple times, etc.

    # Starter, from code used in initial testing in methods.py:
    # response = localhost_session.delete_node('x7s9m')
    # print(response.status_code)
