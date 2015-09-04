import os
import vcr
import requests
from requests.auth import HTTPBasicAuth
from osf_api_v2_client.session import Session
from osf_api_v2_client.settings.local import (AUTH1,
                                              USER1_ID)

# Comment line below prevents unittest from deletion in import optimization
# noinspection PyUnresolvedReferences
import unittest

VCR_CASSETTE_PREFIX = 'fixtures/vcr_cassettes/test_examples/'
VCR_RECORD_MODE = 'new_episodes'

class TestExamples(unittest.TestCase):

    examples_vcr = vcr.VCR(
        cassette_library_dir='{}test_examples'.format(VCR_CASSETTE_PREFIX),
        record_mode=VCR_RECORD_MODE
    )

    @examples_vcr.use_cassette()
    def test_examples(self):
        # TODO get this working
        pass

        # # Session with default root url (currently
        # # https://staging2-api.osf.io/v2/)and no authentication
        # anonymous_session = Session()
        #
        # # Session with custom root url and auth
        # auth_session = Session(
        #     root_url='https://my-api-url.osf.io/v2/',
        #     auth=HTTPBasicAuth('user@example.com', 'password'))
        #
        # s = Session(auth=AUTH1)  # TODO why is auth not being recognized?
        #
        # # Print titles of the first 30 nodes listed in the API
        # for node in s.get_node_generator(num_requested=30):
        #     print(node.attributes.title)
        #
        # # Print names of the first 30 users listed in the API
        # for user in s.get_user_generator(num_requested=30):
        #     print(user.attributes.fullname)
        #
        # root = s.get_root()  # get dotnotator version of root
        # user_id = root.meta.current_user.data.id
        # user = s.get_user(user_id)  # get the user with the given id
        # # TODO why isn't the above working? Alternative approach
        # # below (also doesn't work) :
        # # user_response = requests.get(
        # #     'https://staging2-api.osf.io/v2/users/me/')
        # # user_json = user_response.json()
        # # print(user_json)
        # # user = s.get_user(user_json[u'data'][u'id'])
        #
        # # Download user's gravatar image
        # response = requests.get(user.attributes.gravatar_url)
        # with open("{}_gravatar".format(user.fullname), "wb") as gravatar_file:
        #     gravatar_file.write(response.content)
        #
        # # Get ids of 3 of user's nodes
        # node_generator = s.get_node_generator(
        #     url=user.relationships.nodes.links.related,
        #     num_requested=3
        # )
        # node_list = []
        # for node in node_generator:
        #     node_list.append(node.id)
        #
        # # Print names of all contributors of a node
        # node_id = node_list[0]
        # node = s.get_node(node_id)
        # for contrib in s.get_user_generator(
        #         url=node.relationships.contributors.links.related.href):
        #     print(contrib.attributes.fullname)
        #
        # # Download a node's files
        # for file in s.get_file_generator(node_id):
        #     file_to_download = requests.get(file.links.self)
        #     # Name the new file with the name of the file given in the API
        #     filepath = "myfolder/{}/{}".format(file.provider, file.name)
        #     print("Downloading file: {}".format(filepath))
        #     # Create directory for file if it doesn't exist
        #     os.makedirs(os.path.dirname(filepath), exist_ok=True)
        #     with open(filepath, "wb") as new_file:
        #         new_file.write(file_to_download.content)
