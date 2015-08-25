import requests
import collections


class StatusCode400orGreaterError(Exception):
    """
    Takes a Response object (from the requests library)
    and returns an error explaining that its status_code
    is 400 or greater, and the reason for the status_code.
    """
    def __init__(self, response):
        """
        :param response: a Response object (from the requests library)
        whose status_code is 400 or greater
        """
        self.response = response

    def __str__(self):
        string = ('Error in attempt to access {} \n'
                  'Status code: {} {} \n'
                  'Content: {}'.format(self.response.url,
                                       self.response.status_code,
                                       self.response.reason,
                                       self.response.text))
        return string

def get_response_or_exception(method, url, *args, **kwargs):
    method = method.lower()
    # TODO consider: Possible alternative to replace a bunch of if statements:
    # mydict = {
    #     'get':requests.get
    # }
    # mydict[method](url, *args, **kwargs)
    if method == 'get':
        response = requests.get(url, *args, **kwargs)
    elif method == 'post':
        response = requests.post(url, *args, **kwargs)
    elif method == 'patch':
        response == requests.patch(url, *args, **kwargs)
    elif method == 'delete':
        response == requests.delete(url, **kwargs)
    else:
        raise ValueError('Invalid method input: {} \n'
                         'Please use get, post, patch, or delete.')
    if response.status_code >= 400:
        raise StatusCode400orGreaterError(response)
    else:
        return response


def file_generator(files_url, auth=None, num_requested=-1):
    """
    :param files_url: the url where the desired files are located
    :param auth: authentication to send with the request
    :param num_requested: the number of items desired; if -1, all
    items available will be returned
    :return: a generator of DotNotator versions of the files
    """
    #: Number of items left in the generator
    count_remaining = num_requested
    #: Next url to get the json response from
    url = files_url

    while url is not None:
        files_page = get_response_or_exception('get', url, auth=auth)
        files_page_json = files_page.json()
        for item in files_page_json[u'data']:
            # If it's a folder, follow it
            if item[u'item_type'] == "folder":
                url_to_follow = item[u'links'][u'related']
                for subitem in file_generator(url_to_follow, auth=auth,
                                              num_requested=count_remaining):
                    count_remaining -= 1
                    yield DotNotator(subitem)
            # If it's a file, yield it
            elif item[u'item_type'] == "file":
                if num_requested == -1:
                    yield DotNotator(item)
                elif count_remaining > 0:
                    count_remaining -= 1
                    yield DotNotator(item)
                elif count_remaining == 0:
                    break
        if count_remaining == 0:
            break
        url = files_page_json[u'links'][u'next']


def dotnotator_generator(url, auth=None, num_requested=-1):
    """
    Deals with pagination.
    :param url: the url where the desired items are located
    :param auth: authentication to send with the request
    :param num_requested: the number of items desired; if -1, all
    items available will be returned
    :return: a generator of DotNotator versions of the items desired
    """
    #: Number of items left in the generator
    count_remaining = num_requested
    #: Next url to get the json response from
    url = url  # url of first page

    while url is not None:
        response = get_response_or_exception('get', url, auth=auth)
        response_json = response.json()
        for item in response_json[u'data']:
            if num_requested == -1:
                yield DotNotator(item)
            elif count_remaining > 0:
                count_remaining -= 1
                yield DotNotator(item)
            elif count_remaining == 0:
                break
        if count_remaining == 0:
            break
        url = response_json[u'links'][u'next']


def json_dict_generator(url, auth=None, num_requested=-1):
    # TODO get rid of this method
    """
    Deals with pagination.
    :param url: the url where the desired items are located
    :param auth: authentication to send with the request
    :param num_requested: the number of items desired; if -1, all items
    available will be returned
    :return: a generator of DotNotator versions of the items desired
    """
    #: Number of items left in the generator
    count_remaining = num_requested
    #: Next url to get the json response from
    url = url  # url of first page

    while url is not None:
        response = get_response_or_exception('get', url, auth=auth)
        response_json = response.json()
        data = response_json[u'data']
        for item in data:
            if num_requested == -1:
                yield item
            elif count_remaining > 0:
                count_remaining -= 1
                yield item
            elif count_remaining == 0:
                break
        if count_remaining == 0:
            break
        url = response_json[u'links'][u'next']


class DotNotator(collections.MutableMapping):
    """
    Given a dict, DotNotator makes the dict's data accessible as data
    attributes (using 'dot' notation).

    e.g. given json dictionary json_dict, DotNotator enables access
    like so:
    json_dict.data[0].name
    instead of requiring this syntax:
    json_dict[u'data'][0][u'name']

    Note that both syntaxes will still work, though, and they can
    be mixed:
    json_dict[u'data'][0].name
    json_dict.data[0][u'name']

    As seen in the above example, DotNotator recurses through dicts
    of dicts and lists of dicts, to make those dicts into DotNotator
    objects as well.

    See: http://stackoverflow.com/a/3387975/4979097
    Also modified from: http://stackoverflow.com/a/3031270/4979097
    """

    def __init__(self, dictionary=None):
        if dictionary is None:
            pass  # TODO or raise TypeError ?
        elif isinstance(dictionary, dict):
            for key in dictionary:
                self.__setitem__(key, dictionary[key])
        else:
            raise TypeError('expected dict')

    def __setitem__(self, key, value):
        if isinstance(value, dict):    # DotNotate other dicts in dict
            value = DotNotator(value)
        elif isinstance(value, list):  # DotNotate items in a list of dicts
            new_value = []
            if value:  # if value list is not empty
                if isinstance(value[0], dict):
                    for item in value:
                        new_value.append(DotNotator(item))
                    value = new_value
        self.__dict__[key] = value

    def __getitem__(self, key):
        """
        Note that this returns a KeyError if the user attempts to
        access a nonexistent key. For an example of a __getitem__
        method that instead creates the key and sets its value to
        be an empty DotNotator (well, DotNotator) object, see the
        DotNotator class in a former version of this library:
        https://github.com/jamiehand/osf_api_v2_client/commit/98da3a7dbab5a92fb99342508f90942bfea3cf05
        """
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    __setattr__ = __setitem__
    __getattr__ = __getitem__
