# TODO should I have this?: # -*- coding: utf-8 -*-

import unittest  # TODO tests were failing without this. Why is it gray as if it's not being used?
# import mock
import pprint
from nose.tools import *  # flake8: noqa

from methods import Session

pp = pprint.PrettyPrinter(indent=4)

class TestSessionLocalhost(unittest.TestCase):
    # NOTE: These tests are written to be relative to the localhost:8000 api server,
    # so the values for users and node_id's will change depending on whose computer runs the test.
    def setUp(self):
        # Change these to a public node id, and the id of a private node that was created by USER.
        self.PUBLIC_NODE_ID = 'mrdnb'  # 'abcd3'
        self.PRIVATE_NODE_ID = 'z9npx'  # '12345'

        # Change these to the email and pw of the main user, who created the private node
        self.USER = 'user'
        self.PASS = 'pass'

        # Change these to the email and pw of a second user, who can't see the private node
        self.USER2 = 'user2'
        self.PASS2 = 'pass2'

        # A session authenticated by the user who created the node with PRIVATE_NODE_ID
        self.session_with_auth = Session(
            domain="http://localhost:8000/", api_prefix="v2/",
            user=self.USER, pw=self.PASS
        )
        # A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
        self.session_with_different_auth = Session(
            domain="http://localhost:8000/", api_prefix="v2/",
            user=self.USER2, pw=self.PASS2
        )
        # A session that is not authenticated
        self.session_with_no_auth = Session(
            domain="http://localhost:8000/", api_prefix="v2/"
        )

    # GETTING URL

    def test_url_auth(self):
        assert_equal(self.session_with_auth.url, "http://localhost:8000/v2/")

    def test_url_not_auth(self):
        assert_equal(self.session_with_no_auth.url, "http://localhost:8000/v2/")

    # GETTING ROOT

    def test_get_root_auth(self):
        root = self.session_with_auth.get_root()
        assert_equal(root.status_code, 200)

    def test_get_root_not_auth(self):
        root = self.session_with_no_auth.get_root()
        assert_equal(root.status_code, 200)

    # GETTING NODES

    def test_get_public_node_auth_contrib(self):
        public_node = self.session_with_auth.get_node(self.PUBLIC_NODE_ID)
        assert_equal(public_node.status_code, 200)

    def test_get_public_node_auth_non_contrib(self):
        public_node = self.session_with_different_auth.get_node(self.PUBLIC_NODE_ID)
        assert_equal(public_node.status_code, 200)

    def test_get_public_node_not_auth(self):
        public_node = self.session_with_no_auth.get_node(self.PUBLIC_NODE_ID)
        assert_equal(public_node.status_code, 200)

    def test_get_private_node_auth_contrib(self):
        # The node with PRIVATE_NODE_ID is one created by USER, so it should be visible to USER.
        private_node = self.session_with_auth.get_node(self.PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 200)

    def test_get_private_node_auth_non_contrib(self):
        # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
        private_node = self.session_with_different_auth.get_node(self.PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    def test_get_private_node_not_auth(self):
        # Unauthenticated user should not be able to view any private node.
        private_node = self.session_with_no_auth.get_node(self.PRIVATE_NODE_ID)
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
        # TODO capture the node_id, make it self.PRIVATE_NODE_ID, use it for GET, DELETE tests (& PUT/POST?)
        # TODO including tests that check that non-auth'd users *can't* put/post/delete
        new_public_node = self.session_with_auth.create_node(
            "Creating public node with python 1", category="", public="true"
        )
        # print(new_public_node.status_code)
        # print(new_public_node.json()[u'data'][u'public'])
        assert_true(new_public_node.json()[u'data'][u'public'])

    def test_create_private_node(self):
        # TODO capture the node_id for this, make it self.PRIVATE_NODE_ID, use it for GET, DELETE tests (& PUT/POST?)
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
            self.PUBLIC_NODE_ID,
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
            self.PUBLIC_NODE_ID,
            title="User2's New Title",
            description="User2's new description",
            category=""
        )
        assert_equal(edited_public_node.status_code, 403)
        public_node = self.session_with_different_auth.get_node(self.PUBLIC_NODE_ID)
        assert_equal(public_node.json()[u'data'][u'title'], "User's New Title")
        assert_equal(public_node.json()[u'data'][u'description'], "User's new description")
        assert_equal(public_node.json()[u'data'][u'description'], "")

    # TODO finished?
    def test_edit_public_node_not_auth(self):
        edited_public_node = self.session_with_no_auth.edit_node(
            self.PUBLIC_NODE_ID,
            title="Jamie's New Title",
            description="Jamie's new description",
            category=""
        )
        assert_equal(edited_public_node.status_code, 200)
        assert_equal(edited_public_node.json()[u'data'][u'title'], "Jamie's New Title")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "Jamie's new description")
        assert_equal(edited_public_node.json()[u'data'][u'description'], "")
        edited_public_node = self.session_with_no_auth.edit_node(self.PUBLIC_NODE_ID)
        assert_equal(edited_public_node.status_code, 200)

    # TODO finish
    def test_edit_private_node_auth_contributor(self):
        # The node with PRIVATE_NODE_ID is one created by USER, so it should be visible to USER.
        private_node = self.session_with_auth.edit_node(self.PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 200)

    # TODO finish
    def test_edit_private_node_auth_non_contributor(self):
        # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
        private_node = self.session_with_different_auth.edit_node(self.PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    # TODO finish
    def test_edit_private_node_not_auth(self):
        # Unauthenticated user should not be able to view any private node.
        private_node = self.session_with_no_auth.edit_node(self.PRIVATE_NODE_ID)
        assert_equal(private_node.status_code, 403)

    # DELETING NODES
    # TODO write tests on deleting nodes (private, public; auth, diff_auth, not_auth
    # TODO check if Reina fixed problem of deleted nodes being returned, ability to delete nodes multiple times, etc.

    # Starter, from code used in initial testing in methods.py:
    # response = localhost_session.delete_node('x7s9m')
    # print(response.status_code)


# class TestSessionStaging2(unittest.TestCase):
#     # STAGING2 TESTS - TODO do we need these? I'll write most of my tests for localhost for now.
#     def setUp(self):
#         # Change these to a public node id, and the id of a private node that was created by USER.
#         self.PUBLIC_NODE_ID = 'bxsu6'  # 'abcd3'
#         self.PRIVATE_NODE_ID = '12345'
#
#         # Change these to the email and pw of the main user, who created the private node
#         self.USER = 'user'
#         self.PASS = 'pass'
#
#         # Change these to the email and pw of a second user, who can't see the private node
#         self.USER2 = 'user2'
#         self.PASS2 = 'pass2'
#
#         # A staging2 session authenticated by the user who created the node with PRIVATE_NODE_ID
#         self.session_with_auth = Session(user=self.USER, pw=self.PASS)
#
#     def test_url(self):
#         assert_equal(self.session_with_auth.url, "https://staging2.osf.io/api/v2/")
#
#     def test_get_root(self):
#         root = self.session_with_auth.get_root()
#         assert_equal(root.status_code, 200)
#
#     def test_get_node(self):
#         node = self.session_with_auth.get_node(self.PUBLIC_NODE_ID)
#         assert_equal(node.status_code, 200)
