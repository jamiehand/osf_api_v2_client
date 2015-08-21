# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth?

from six import string_types
import vcr
import types
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
from osf_api_v2_client.utils import DotNotator


CASSETTE_PREFIX = '../tests/fixtures/vcr_cassettes/test_users/'

# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)


class TestGetUsers(unittest.TestCase):

    get_users_vcr = vcr.VCR(
        cassette_library_dir='{}test_get_users'.format(CASSETTE_PREFIX),
        record_mode='new_episodes',  # TODO or 'once' ?
    )

    @get_users_vcr.use_cassette()
    def test_get_user_generator(self):
        user_generator = SESSION_AUTH1.get_user_generator()
        # TODO what should my assertion(s) here be?
        assert_true(isinstance(user_generator, types.GeneratorType))
        # count = 1
        # for node in node_generator:
        #     print("***************************** {} *******************************".format(count))
        #     pp.pprint(node)
        #     count += 1

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


class TestUserAttributes(unittest.TestCase):
    """
    Test accessing user attributes with the DotNotator format,
    as enabled through the DotNotator class in osf_api_v2_client/utils.py
    """
    # TODO rename this class when Dawn's PR is merged, if needed.
    # TODO more tests here; modify to match Dawn's PR once merged.

    user_attributes_vcr = vcr.VCR(
        cassette_library_dir='{}test_user_attributes'.format(CASSETTE_PREFIX),
        record_mode='new_episodes',  # TODO or 'once' ?
    )

    @user_attributes_vcr.use_cassette()
    def setUp(self):
        self.user = SESSION_AUTH1.get_user(USER1_ID)

    def test_user_names(self):
        """
        Ensure that the names return strings
        """
        # TODO could test, e.g. assert_true(self.user.fullname == self[u'user'][u'fullname'])
        fullname = self.user.fullname
        assert_true(isinstance(fullname, string_types))
        given_name = self.user.given_name
        assert_true(isinstance(given_name, string_types))
        middle_name = self.user.middle_name
        assert_true(isinstance(middle_name, string_types))
        family_name = self.user.family_name
        assert_true(isinstance(family_name, string_types))
        suffix = self.user.suffix
        assert_true(isinstance(suffix, string_types))

    def test_gravatar_url(self):
        """
        Ensures user.gravatar_url returns a valid url
        """
        url = self.user.gravatar_url
        response = requests.get(url)
        assert_equal(response.status_code, 200)

    def test_employment_institutions(self):
        """
        Ensures user.employment_institutions returns a list of DotNotator objects,
        and that getting information from the objects works.
        """
        employment_list = self.user.employment_institutions
        assert_true(isinstance(employment_list, list))
        if employment_list:  # if employment_list is not empty
            assert_true(isinstance(employment_list[0], DotNotator))
            start_year = employment_list[0].startYear
            assert_true(isinstance(start_year, string_types))
            ongoing = employment_list[0].ongoing
            assert_true(isinstance(ongoing, bool))

    def test_educational_institutions(self):
        """
        Ensures user.educational_institutions returns a list of DotNotator objects,
        and that getting information from the objects works.
        """
        educational_list = self.user.educational_institutions
        assert_true(isinstance(educational_list, list))
        if educational_list:  # if educational_list is not empty
            assert_true(isinstance(educational_list[0], DotNotator))
            start_year = educational_list[0].startYear
            assert_true(isinstance(start_year, string_types))
            ongoing = educational_list[0].ongoing
            assert_true(isinstance(ongoing, bool))

    def test_social_accounts(self):
        social_dict = self.user.social_accounts
        assert_true(isinstance(social_dict, DotNotator))

