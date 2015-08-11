# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth

import six
import vcr
import types
import unittest
from nose.tools import *  # flake8: noqa

from osf_api_v2_client.utils import DotDictify
from osf_api_v2_client.session import Session

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

my_vcr = vcr.VCR(
    cassette_library_dir='fixtures/vcr_cassettes',
    record_mode='new_episodes',  # TODO or 'once' ?; for re-recording: 'all'
)


class TestGetNodes(unittest.TestCase):

    @my_vcr.use_cassette()
    def test_get_node_generator(self):
        node_generator = SESSION_AUTH1.get_node_generator(num_requested=25)
        # TODO what should my assertion(s) here be?
        assert_true(isinstance(node_generator, types.GeneratorType))
        # Create a list with the nodes in it
        node_list = []
        for node in node_generator:
            node_list.append(node)
        assert_equal(len(node_list), 25)
        print(type(node_list[0]))
        # assert_true(isinstance(node_list[0], DotDictify))
        # count = 1
        # for node in node_generator:
        #     print("***************************** {} *******************************".format(count))
        #     pp.pprint(node)
        #     count += 1
        node = SESSION_AUTH1.get_node('2bwm8')
        print(type(node))

    # TODO could createfakes for USER1 with some private nodes, some public nodes and make sure node_generator
    # returns more nodes when USER1 calls node_generator().

    @my_vcr.use_cassette()
    def test_get_public_node_auth_contrib(self):
        public_node = SESSION_AUTH1.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, DotDictify))

    @my_vcr.use_cassette()
    def test_get_public_node_auth_non_contrib(self):
        public_node = SESSION_AUTH2.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, DotDictify))

    @my_vcr.use_cassette()
    def test_get_public_node_not_auth(self):
        public_node = SESSION_NO_AUTH.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, DotDictify))

    # TODO is there a way for vcrpy to record the exceptions to replay them? right now these 3 tests fail:
    @my_vcr.use_cassette()
    def test_get_private_node_auth_contrib(self):
        # The node with PRIVATE_NODE_ID is one created by USER1, so it should be visible to USER1.
        private_node = SESSION_AUTH1.get_node(PRIVATE_NODE_ID)
        assert_true(isinstance(private_node, DotDictify))

    @my_vcr.use_cassette()
    def test_get_private_node_auth_non_contrib(self):
        # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
        with assert_raises(Exception):  # TODO more specific exception?
            SESSION_AUTH2.get_node(PRIVATE_NODE_ID)

    @my_vcr.use_cassette()
    def test_get_private_node_not_auth(self):
        # Unauthenticated user should not be able to view any private node.
        with assert_raises(Exception):  # TODO more specific exception?
            SESSION_NO_AUTH.get_node(PRIVATE_NODE_ID)


# class TestCreateNodes(unittest.TestCase):
#     # TODO add checks into tests to make sure the title, public, etc. are correct?
#
#     # def test_create_public_node_auth(self):
#     #     # TODO figure out how to do this.
#     #     # TODO capture the node_id, make it PRIVATE_NODE_ID, use it for GET, DELETE tests (& PATCH?)
#     #     # TODO include tests that check that non-auth'd users *can't* patch/post/delete
#     #     new_public_node = SESSION_AUTH1.create_node(
#     #         "Creating public node with python 1", category="", public="true"
#     #     )
#     #     # print(new_public_node.status_code)
#     #     # print(new_public_node.json()[u'data'][u'public'])
#     #     assert_true(new_public_node.json()[u'data'][u'public'])
#
#     def test_create_private_node(self):
#         # TODO capture the node_id for this, make it PRIVATE_NODE_ID, use it for GET, DELETE tests (& PATCH?)
#         # TODO include tests that check that non-auth'd users *can't* patch/post/delete/get
#         new_private_node = SESSION_AUTH1.create_node(
#             "Creating private node with python 1", category=""
#         )
#         assert_true(isinstance(new_private_node, DotDictify))
#
#     def test_create_node_not_auth(self):
#         # Shouldn't work, because users must be authenticated in order to create nodes.
#         # with assert_raises ??
#         new_private_node = SESSION_NO_AUTH.create_node(
#             "Creating private node with python 1", category=""
#         )
#         assert_equal(new_private_node.status_code, 403)  # forbidden status code
#
#
# class TestEditNodes(unittest.TestCase):
#
#     # TODO finished?
#     # TODO change this to modify the public node created by test_create_public_node
#     def test_edit_public_node_auth_contrib(self):
#         edited_public_node = SESSION_AUTH1.edit_node(
#             PUBLIC_NODE_ID,
#             title="User's New Title",
#             description="User's new description",
#             category=""
#         )
#         assert_equal(edited_public_node.status_code, 200)
#         assert_equal(edited_public_node.json()[u'data'][u'title'], "Jamie's New Title")
#         assert_equal(edited_public_node.json()[u'data'][u'description'], "Jamie's new description")
#         assert_equal(edited_public_node.json()[u'data'][u'description'], "")
#
#     # TODO finished?
#     def test_edit_public_node_auth_non_contrib(self):
#         edited_public_node = SESSION_AUTH2.edit_node(
#             PUBLIC_NODE_ID,
#             title="User2's New Title",
#             description="User2's new description",
#             category=""
#         )
#         assert_equal(edited_public_node.status_code, 403)
#         public_node = SESSION_AUTH2.get_node(PUBLIC_NODE_ID)
#         assert_equal(public_node.json()[u'data'][u'title'], "User's New Title")
#         assert_equal(public_node.json()[u'data'][u'description'], "User's new description")
#         assert_equal(public_node.json()[u'data'][u'description'], "")
#
#     # TODO finished?
#     def test_edit_public_node_not_auth(self):
#         edited_public_node = SESSION_NO_AUTH.edit_node(
#             PUBLIC_NODE_ID,
#             title="Jamie's New Title",
#             description="Jamie's new description",
#             category=""
#         )
#         assert_equal(edited_public_node.status_code, 200)
#         assert_equal(edited_public_node.json()[u'data'][u'title'], "Jamie's New Title")
#         assert_equal(edited_public_node.json()[u'data'][u'description'], "Jamie's new description")
#         assert_equal(edited_public_node.json()[u'data'][u'description'], "")
#         edited_public_node = SESSION_NO_AUTH.edit_node(PUBLIC_NODE_ID)
#         assert_equal(edited_public_node.status_code, 200)
#
#     # TODO finish
#     def test_edit_private_node_auth_contributor(self):
#         # The node with PRIVATE_NODE_ID is one created by USER1, so it should be visible to USER1.
#         private_node = SESSION_AUTH1.edit_node(PRIVATE_NODE_ID)
#         assert_equal(private_node.status_code, 200)
#
#     # TODO finish
#     def test_edit_private_node_auth_non_contributor(self):
#         # USER2 is not a contributor to the node with PRIVATE_NODE_ID, so it should not be visible.
#         private_node = SESSION_AUTH2.edit_node(PRIVATE_NODE_ID)
#         assert_equal(private_node.status_code, 403)
#
#     # TODO finish
#     def test_edit_private_node_not_auth(self):
#         # Unauthenticated user should not be able to view any private node.
#         private_node = SESSION_NO_AUTH.edit_node(PRIVATE_NODE_ID)
#         assert_equal(private_node.status_code, 403)
#
# class TestDeleteNodes(unittest.TestCase):
#
#     pass
#     # TODO write tests on deleting nodes (private, public; auth, diff_auth, not_auth
#     # TODO check if Reina fixed problem of deleted nodes being returned, ability to delete nodes multiple times, etc.
#
#     # Starter, from code used in initial testing:
#     # response = localhost_session.delete_node('x7s9m')
#     # print(response.status_code)
