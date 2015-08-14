import six
import vcr
import types
import timeit
import pprint
import unittest
import requests
from nose.tools import *  # flake8: noqa

import os
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
from osf_api_v2_client.utils import (DotDictify,
                                     dotdictify_generator,
                                     file_generator,
                                     get_response_or_exception)

# Sessions with different forms of authentication:
# A session authenticated by the user who created the node with PRIVATE_NODE_ID
SESSION_AUTH1 = Session(root_url=URL, auth=AUTH1)
# A session authenticated by a user who does NOT have access to the node with PRIVATE_NODE_ID
SESSION_AUTH2 = Session(root_url=URL, auth=AUTH2)
# A session that is not authenticated
SESSION_NO_AUTH = Session(root_url=URL)

my_vcr = vcr.VCR(
    cassette_library_dir='fixtures/vcr_cassettes/test_utils',
    record_mode='new_episodes',  # TODO or 'once' ?
)

# TODO get rid of pprint, smart_print()
pp = pprint.PrettyPrinter()
def smart_print(string):
    try:
        print(string)
    except UnicodeEncodeError:
        print(string.encode('utf-8'))


class TestFileGenerator(unittest.TestCase):

    @my_vcr.use_cassette()
    def test_few_files(self):
        for file in SESSION_AUTH1.get_file_generator(PUBLIC_NODE_ID):
            file_to_download = requests.get(file.links.self)
            filepath = "test_file_generator/test_few_files/{}/{}".format(file.provider, file.name)
            print("Downloading file: {}".format(filepath))
            os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Create directory for file if it doesn't exist
            # Name the new file with the name of the file given in the API
            with open(filepath, "wb") as new_file:
                new_file.write(file_to_download.content)
    # TODO how to assert that files exist?



class TestDotDictifyGenerator(unittest.TestCase):

    @my_vcr.use_cassette()
    def test_defaults(self):
        """
        num_requested should == -1, meaning all items should be returned
        """
        big_gen = dotdictify_generator("https://staging2.osf.io/api/v2/users/se6py/nodes/")
        with assert_raises(StopIteration):
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))
            print(next(big_gen))

    @my_vcr.use_cassette()
    def test_num_requested_negative1(self):
        # TODO this
        """
        Test that generator responds correctly when num_requested == -1 vs any other number.
        """
        pass

    @my_vcr.use_cassette()
    def test_num_requested_positive(self):
        """
        request 4; 4 items should be returned
        """
        happy_gen = dotdictify_generator("https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive",
                                       num_requested=4)
        for item in happy_gen:
            print("{}: {}: {}".format(item.provider, item.name, item.links.self))

    def test_time(self):
        small_gen = dotdictify_generator("https://staging2.osf.io/api/v2/users",
                                       num_requested=4)

        def bar():
            for item in small_gen:
                print(item)

        print(timeit.timeit(bar))

        big_gen = dotdictify_generator("https://staging2.osf.io/api/v2/users")

        def foo():
            for item in big_gen:
                print(item)

        print(timeit.timeit(foo))


