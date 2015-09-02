import pprint
import types

import vcr
from nose.tools import *  # flake8: noqa

# Comment line below prevents unittest from deletion in import optimization
# noinspection PyUnresolvedReferences
import unittest

from osf_api_v2_client.utils import (
    DotNotator,
    StatusCode400orGreaterError
)
from osf_api_v2_client.session import Session
from osf_api_v2_client.settings.local import (
    URL,                # e.g. 'https://staging2.osf.io/api/v2/'
    AUTH1,              # authentication details for USER1
    AUTH2,              # authentication details for USER2
    PUBLIC_NODE_ID,     # id of a public node
    PRIVATE_NODE_ID     # id of a private node that is visible to USER1 but
                        # *not* to USER2
)

pp = pprint.PrettyPrinter(indent=4)

# Sessions with different forms of authentication:
# A session authenticated by the user who created the node
# with PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access
# to the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)


VCR_CASSETTE_PREFIX = 'fixtures/vcr_cassettes/test_nodes/'
VCR_RECORD_MODE = 'new_episodes'


# TODO once functionality exists to create public nodes and edit
# a node's private/public setting, add tests for this functionality
# under TestCreateNodes and TestEditNodes.


class TestGetNodes(unittest.TestCase):

    get_nodes_vcr = vcr.VCR(
        cassette_library_dir='{}test_get_nodes'.format(VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @get_nodes_vcr.use_cassette()
    def test_get_node_generator(self):
        node_generator = SESSION_AUTH1.get_node_generator(num_requested=25)
        assert_true(isinstance(node_generator, types.GeneratorType))
        node_list = []  # Create a list with the nodes in it
        for node in node_generator:
            node_list.append(node)
        assert_equal(len(node_list), 25)
        assert_true(isinstance(node_list[0], DotNotator))

    @get_nodes_vcr.use_cassette()
    def test_get_public_node_auth_contrib(self):
        public_node = SESSION_AUTH1.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, DotNotator))

    @get_nodes_vcr.use_cassette()
    def test_get_public_node_auth_non_contrib(self):
        public_node = SESSION_AUTH2.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, DotNotator))

    @get_nodes_vcr.use_cassette()
    def test_get_public_node_no_auth(self):
        public_node = SESSION_NO_AUTH.get_node(PUBLIC_NODE_ID)
        assert_true(isinstance(public_node, DotNotator))

    @get_nodes_vcr.use_cassette()
    def test_get_private_node_auth_contrib(self):
        """
        The node with PRIVATE_NODE_ID is one created by USER1,
        so it should be visible to USER1.
        """
        private_node = SESSION_AUTH1.get_node(PRIVATE_NODE_ID)
        assert_true(isinstance(private_node, DotNotator))

    @get_nodes_vcr.use_cassette()
    def test_get_private_node_auth_non_contrib(self):
        """
        USER2 is not a contributor to the node with PRIVATE_NODE_ID,
        so it should not be visible.
        """
        with assert_raises(StatusCode400orGreaterError):
            SESSION_AUTH2.get_node(PRIVATE_NODE_ID)

    @get_nodes_vcr.use_cassette()
    def test_get_private_node_no_auth(self):
        """
        Unauthenticated user should not be able to view any
        private node.
        """
        with assert_raises(StatusCode400orGreaterError):
            SESSION_NO_AUTH.get_node(PRIVATE_NODE_ID)


class TestCreateNodes(unittest.TestCase):

    create_nodes_vcr = vcr.VCR(
        cassette_library_dir='{}test_create_nodes'.format(VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @create_nodes_vcr.use_cassette()
    def test_create_private_node_all_params(self):
        new_private_node = SESSION_AUTH1.create_node(
            "Private node created with client library", category="",
            description="Hello world!"
        )
        assert_true(isinstance(new_private_node, DotNotator))
        assert_equal(new_private_node.title,
                     "Private node created with client library")
        assert_equal(new_private_node.category, "")
        assert_equal(new_private_node.description, "Hello world!")

    @create_nodes_vcr.use_cassette()
    def test_create_private_nodes_title_param_only(self):
        new_private_node = SESSION_AUTH1.create_node(
            "Private node 2 created with client library"
        )
        assert_true(isinstance(new_private_node, DotNotator))
        assert_equal(new_private_node.title,
                     "Private node 2 created with client library")
        assert_equal(new_private_node.category, "")
        assert_equal(new_private_node.description, "")

    @create_nodes_vcr.use_cassette()
    def test_create_private_node_no_auth(self):
        """
        Should not work, because users must be authenticated
        in order to create nodes.
        """
        with assert_raises(StatusCode400orGreaterError):
            new_private_node = SESSION_NO_AUTH.create_node(
                "Private node 3 created with client library"
            )


class TestEditNodes(unittest.TestCase):

    edit_nodes_vcr = vcr.VCR(
        cassette_library_dir='{}test_edit_nodes'.format(VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @edit_nodes_vcr.use_cassette()
    def setUp(self):
        # TODO this setUp is currently dependent on edit_node() working.
        # How can we make it independent?
        SESSION_AUTH1.edit_node(
            PUBLIC_NODE_ID,
            title="Original public node title",
            description="Original public node description",
            category=""
        )
        SESSION_AUTH1.edit_node(
            PRIVATE_NODE_ID,
            title="Original private node title",
            description="Original private node description",
            category=""
        )

    @edit_nodes_vcr.use_cassette()
    def test_edit_public_node_auth_contrib(self):
        """
        The node with PUBLIC_NODE_ID was created by USER1,
        so it should be editable by USER1.
        """
        edited_public_node = SESSION_AUTH1.edit_node(
            PUBLIC_NODE_ID,
            title="User1's new title",
            description="User1's new description",
            category="data"
        )
        assert_true(isinstance(edited_public_node, DotNotator))
        assert_equal(edited_public_node.title,
                     "User1's new title")
        assert_equal(edited_public_node.description,
                     "User1's new description")
        assert_equal(edited_public_node.category,
                     "data")

    @edit_nodes_vcr.use_cassette()
    def test_edit_public_node_auth_non_contrib(self):
        """
        USER2 is not a contributor to the node with PUBLIC_NODE_ID,
        so it should not be editable by USER2.
        """
        with assert_raises(StatusCode400orGreaterError):
            edited_public_node = SESSION_AUTH2.edit_node(
                PUBLIC_NODE_ID,
                title="User2's new title",
                description="User2's new description",
                category="data",
            )

    @edit_nodes_vcr.use_cassette()
    def test_edit_public_node_no_auth(self):
        """
        The node with PUBLIC_NODE_ID should be visible to
        a session with no authentication, but should not
        be editable by such a session.
        """
        with assert_raises(StatusCode400orGreaterError):
            edited_public_node = SESSION_NO_AUTH.edit_node(
                PUBLIC_NODE_ID,
                title="NoAuth's new title",
                description="NoAuth's new description",
                category="data",
            )

    @edit_nodes_vcr.use_cassette()
    def test_edit_private_node_auth_contributor(self):
        """
        The node with PRIVATE_NODE_ID was created by USER1,
        so it should be editable by USER1.
        """
        private_node = SESSION_AUTH1.edit_node(
            PRIVATE_NODE_ID,
            title="User1's new title",
            description="User1's new description",
            category="data",
        )
        assert_true(isinstance(private_node, DotNotator))
        assert_equal(private_node.title,
                     "User1's new title")
        assert_equal(private_node.description,
                     "User1's new description")
        assert_equal(private_node.category,
                     "data")

    @edit_nodes_vcr.use_cassette()
    def test_edit_private_node_auth_non_contributor(self):
        """
        USER2 is not a contributor to the node with PRIVATE_NODE_ID,
        so the node should not be visible.
        """
        with assert_raises(StatusCode400orGreaterError):
            private_node = SESSION_AUTH2.edit_node(
                PRIVATE_NODE_ID,
                title="User2's new title",
                description="User2's new description",
                category="data",
            )

    @edit_nodes_vcr.use_cassette()
    def test_edit_private_node_no_auth(self):
        """
        Unauthenticated user should not be able to view any
        private node.
        """
        with assert_raises(StatusCode400orGreaterError):
            private_node = SESSION_NO_AUTH.edit_node(
                PRIVATE_NODE_ID,
                title="NoAuth's new title",
                description="NoAuth's new description",
                category="data",
            )


class TestDeleteNodes(unittest.TestCase):

    delete_nodes_vcr = vcr.VCR(
        cassette_library_dir='{}test_delete_nodes'.format(VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @delete_nodes_vcr.use_cassette()
    def setUp(self):
        # This is currently the id of a node that I created and made
        # public in the GUI, but to make the test self-contained:
        # TODO once it's possible to create public nodes, create
        # a public node with SESSION_AUTH1, recording its id as
        # self.public_node_id, and then delete it in test methods,
        # as done below with the private node.
        self.public_node_id = 'my3kd'

        private_node = SESSION_AUTH1.create_node('Private node to delete')
        self.private_node_id = private_node.id

    @delete_nodes_vcr.use_cassette()
    def test_delete_public_node_auth_non_contrib(self):
        """
        USER2 is not a contributor to the node with
        self.public_node_id, so it should not be deletable by USER2.
        """
        with assert_raises(StatusCode400orGreaterError):
            SESSION_AUTH2.delete_node(
                self.public_node_id
            )

    @delete_nodes_vcr.use_cassette()
    def test_delete_public_node_no_auth(self):
        """
        Unauthenticated user should not be able to delete any node.
        """
        with assert_raises(StatusCode400orGreaterError):
            SESSION_NO_AUTH.delete_node(
                self.public_node_id
            )

    @delete_nodes_vcr.use_cassette()
    def test_delete_public_node_auth_contrib(self):
        """
        The node with self.public_node_id was created by USER1,
        so it should be deletable by USER1.
        """
        SESSION_AUTH1.delete_node(
            self.public_node_id
        )
        with assert_raises(StatusCode400orGreaterError):
            SESSION_AUTH1.get_node(self.public_node_id)

    @delete_nodes_vcr.use_cassette()
    def test_delete_private_node_auth_non_contrib(self):
        """
        USER2 is not a contributor to the node with
        self.private_node_id, so the node should not be visible.
        """
        with assert_raises(StatusCode400orGreaterError):
            SESSION_AUTH2.delete_node(
                self.private_node_id
            )

    @delete_nodes_vcr.use_cassette()
    def test_delete_private_node_no_auth(self):
        """
        Unauthenticated user should not be able to delete any node.
        """
        with assert_raises(StatusCode400orGreaterError):
            SESSION_NO_AUTH.delete_node(
                self.private_node_id
            )

    @delete_nodes_vcr.use_cassette()
    def test_delete_private_node_auth_contrib(self):
        """
        The node with self.private_node_id was created by USER1,
        so it should be deletable by USER1.
        """
        SESSION_AUTH1.delete_node(
            self.private_node_id
        )
        with assert_raises(StatusCode400orGreaterError):
            SESSION_AUTH1.get_node(self.private_node_id)
