import six
import requests
import collections

# Possible alternative to replace a bunch of if statements:
# mydict = {
#     'get':requests.get
# }
# mydict[method](url, *args, **kwargs)
def get_response_or_exception(method, url, *args, **kwargs):
    method = method.lower()
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
        raise Exception('Error in attempt to access {} \n'  # TODO make exception more specific?
                        'Status code: {} {} \n'
                        'Content: {}'.format(
                        response.url, response.status_code, response.reason, response.text))
    else:
        return response  # TODO return DotDictify object instead? -- not now; might stop DotDictifying things later?


def file_generator(files_url, auth=None, num_requested=-1):
    """
    :param files_url: the url where the desired files are located
    :param auth: authentication to send with the request
    :param num_requested: the number of items desired; if -1, all items available will be returned
    :return: a generator of DotDictify versions of the files
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
                for subitem in file_generator(url_to_follow, auth=auth, num_requested=count_remaining):
                    count_remaining -= 1
                    yield DotDictify(subitem)
            # If it's a file, yield it
            elif item[u'item_type'] == "file":
                if num_requested == -1:
                    yield DotDictify(item)
                elif count_remaining > 0:
                    count_remaining -= 1
                    yield DotDictify(item)
                elif count_remaining == 0:
                    break
        if count_remaining == 0:
            break
        url = files_page_json[u'links'][u'next']


def dotdictify_generator(url, auth=None, num_requested=-1):
    """
    Deals with pagination.
    :param url: the url where the desired items are located
    :param auth: authentication to send with the request
    :param num_requested: the number of items desired; if -1, all items available will be returned
    :return: a generator of DotDictify versions of the items desired
    """
    #: Number of items left in the generator
    count_remaining = num_requested
    #: Next url to get the json response from
    url = url  # url of first page

    while url is not None:
        response = get_response_or_exception('get', url, auth=auth)  # page response
        response_json = response.json()
        for item in response_json[u'data']:
            if num_requested == -1:
                yield DotDictify(item)
            elif count_remaining > 0:
                count_remaining -= 1
                yield DotDictify(item)
            elif count_remaining == 0:
                break
        if count_remaining == 0:
            break
        url = response_json[u'links'][u'next']


class DotDictify(dict):
    """
    Given a dictionary, DotDictify makes the dictionary's data accessible as data attributes.
    
    e.g. given json dictionary json_dict, DotDictify enables access like so:
    json_dict.data[0].name
    instead of requiring this syntax:
    json_dict[u'data'][0][u'name']

    Note that both syntaxes will still work, though, and they can be mixed:
    json_dict[u'data'][0].name
    json_dict.data[0][u'name']

    As seen in the above example, DotDictify recurses through dictionaries of dictionaries and lists of
    dictionaries, to make those dictionaries into DotDictify objects as well.

    DocDictify class is modified from here: http://stackoverflow.com/a/3031270/4979097
    """

    marker = object()  # marker is used in __getitem__

    def __init__(self, data=None):
        dict.__init__(self)  # instantiating a dict   # TODO necessary/useful? (see
        # http://stackoverflow.com/questions/2033150/subclassing-dict-should-dict-init-be-called)
        if data is None:
            pass
        elif isinstance(data, dict):
            for key in data:
                self.__setitem__(key, data[key])
        else:
            raise TypeError('expected dict')

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, DotDictify):  # 2nd isinstance prevents infinite recursion
            value = DotDictify(value)
        elif isinstance(value, list):
            new_value = []
            if value:                            # If value list is not empty,
                if isinstance(value[0], dict):   # if list is list of dicts,
                    # TODO can I assume that they will all be dicts if the first is?
                    for i in range(len(value)):  # DotDictify the items in the list
                        new_value.append(DotDictify(value[i]))
                    value = new_value
        super(DotDictify, self).__setitem__(key, value)  # calling dict's setitem

    def __getitem__(self, key):
        """
        A note on the use of 'marker' and 'found' here. Much of this is not my (jamiehand's) code originally,
        so I am not 100% sure about this, but it seems like the only purpose of 'DotDictify.marker'
        and this method's local variable 'found' is to enable special functionality when the user
        attempts to access a key that is not in a DotDictify object. Together, 'DotDictify.marker'
        and 'found' make it so that instead of just returning a KeyError, __getitem__ adds that key and
        creates a new empty DotDictify object as the value for that key.

        The inline comments below are mine, not the original author's.
        """
        found = self.get(key, DotDictify.marker)  # i.e. found = self[key] if key in self, else DotDictify.marker
        if found is DotDictify.marker:                       # If key not in self,
            found = DotDictify()                             # create a new DotDictify object,
            super(DotDictify, self).__setitem__(key, found)  # and set self[key] to be that object (found).
        return found

    __setattr__ = __setitem__
    __getattr__ = __getitem__


class DotNotator(collections.MutableMapping):
    """
    Given a dict, DotNotator makes the dict's data accessible as data attributes
    (using 'dot' notation).

    e.g. given json dictionary json_dict, DotDictify enables access like so:
    json_dict.data[0].name
    instead of requiring this syntax:
    json_dict[u'data'][0][u'name']

    Note that both syntaxes will still work, though, and they can be mixed:
    json_dict[u'data'][0].name
    json_dict.data[0][u'name']

    As seen in the above example, DotNotator recurses through dicts of dicts and
    lists of dicts, to make those dicts into DotNotator objects as well.

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
        elif isinstance(value, list):  # DotNotate the items in a list of dicts
            new_value = []
            if value:  # if value list is not empty
                if isinstance(value[0], dict):
                    for item in value:
                        new_value.append(DotNotator(item))
                    value = new_value
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    __setattr__ = __setitem__
    __getattr__ = __getitem__



