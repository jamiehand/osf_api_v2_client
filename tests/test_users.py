from six import string_types
import vcr
import types
import requests
from nose.tools import *  # flake8: noqa

# Comment line below prevents unittest from deletion in import optimization
# noinspection PyUnresolvedReferences
import unittest

from osf_api_v2_client.settings.local import (
    URL,                # e.g. 'https://staging2-api.osf.io/v2/'
    AUTH1,              # authentication details for USER1
    AUTH2,              # authentication details for USER2
    USER1_ID,           # id of USER1
    USER2_ID,           # id of USER2
)
from osf_api_v2_client.session import Session
from osf_api_v2_client.utils import DotNotator

VCR_CASSETTE_PREFIX = 'fixtures/vcr_cassettes/test_users/'
VCR_RECORD_MODE = 'new_episodes'

# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with
# PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to
# the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)


class TestGetUsers(unittest.TestCase):

    get_users_vcr = vcr.VCR(
        cassette_library_dir='{}test_get_users'.format(VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @get_users_vcr.use_cassette()
    def test_get_user_generator(self):
        user_generator = SESSION_AUTH1.get_user_generator()
        user_list = []
        assert_true(isinstance(user_generator, types.GeneratorType))
        for user in user_generator:
            user_list.append(user.id)
        assert_equal(len(user_list), 50)

    @get_users_vcr.use_cassette()
    def test_get_user_generator_with_num_requested(self):
        user_generator = SESSION_AUTH1.get_user_generator(
            num_requested=5
        )
        user_list = []
        for user in user_generator:
            user_list.append(user.id)
        assert_equal(len(user_list), 5)

    @get_users_vcr.use_cassette()
    def test_get_authenticated_user(self):
        user1 = SESSION_AUTH1.get_user(USER1_ID)
        assert_true(isinstance(user1, DotNotator))

    @get_users_vcr.use_cassette()
    def test_get_different_user_from_authenticated_user(self):
        user2 = SESSION_AUTH1.get_user(USER2_ID)
        assert_true(isinstance(user2, DotNotator))

    @get_users_vcr.use_cassette()
    def test_get_user_from_unauthenticated_session(self):
        user1 = SESSION_NO_AUTH.get_user(USER1_ID)
        assert_true(isinstance(user1, DotNotator))


class TestUserData(unittest.TestCase):
    """
    Test accessing user data with the DotNotator format,
    as enabled through the DotNotator class in osf_api_v2_client/utils.py
    """

    user_data_vcr = vcr.VCR(
        cassette_library_dir='{}test_user_attributes'.format(
            VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @user_data_vcr.use_cassette()
    def setUp(self):
        self.user = SESSION_AUTH1.get_user(USER1_ID)

    def test_id(self):
        assert_equal(self.user.id, USER1_ID)

    def test_type(self):
        assert_equal(self.user.type, u'users')

    def test_attributes(self):
        """
        Ensure that attributes return strings
        """
        for attribute in self.user.attributes:
            assert_true(isinstance(attribute, string_types))

    @user_data_vcr.use_cassette()
    def test_gravatar_url(self):
        """
        Ensures user.gravatar_url returns a valid url
        """
        url = self.user.attributes.gravatar_url
        response = requests.get(url)
        assert_equal(response.status_code, 200)

    @user_data_vcr.use_cassette()
    def test_relationships(self):
        url = self.user.relationships.nodes.links.related
        response = requests.get(url)
        assert_equal(response.status_code, 200)

    @user_data_vcr.use_cassette()
    def test_links_self(self):
        url = self.user.links.self
        response = requests.get(url)
        assert_equal(response.status_code, 200)

    @user_data_vcr.use_cassette()
    def test_links_html(self):
        url = self.user.links.html
        response = requests.get(url)
        assert_equal(response.status_code, 200)
