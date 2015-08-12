import six
import requests


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


def file_generator(url, auth=None, num_requested=-1):
    """
    :param url: the url where the desired items are located
    :param auth: authentication to send with the request
    :param num_requested: the number of items desired; if -1, all items available will be returned
    :return: a generator of Response objects
    """
    #: Number of items left in the generator
    count_remaining = num_requested
    #: Next url to get the json response from
    url = url  # url of first page

    while url is not None:
        files_page = get_response_or_exception('get', url, auth=auth)
        files_page_json = files_page.json()
        for item in files_page_json[u'data']:
            # If it's a folder, follow it
            if item[u'item_type'] == "folder":
                for subitem in file_generator(url, auth=auth, num_requested=count_remaining):
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


# Instead of translating request into json request format, DotDictify transforms response itself.
# TODO seems like it would be more efficient to just translate the request as opposed to transforming the
# response ... unless we can transform the responses on a when-needed basis...?
# DocDictify class is modified from here: http://stackoverflow.com/a/3031270/4979097
class DotDictify(dict):
    """
    Given a dictionary, DotDictify makes the dictionary's data accessible as data attributes.
    e.g. given json dictionary json_dict, DotDictify enables access like so: json_dict.data[0].name
    instead of requiring this syntax: json_dict[u'data'][0][u'name']
    As seen in the above example, DotDictify recurses through dictionaries of dictionaries and lists of
    dictionaries, to make those dictionaries into DotDictify objects as well.
    """
    marker = object()  # a new object  # TODO what does this do...?

    def __init__(self, data=None):
        dict.__init__(self)  # TODO necessary/useful? (see
        # http://stackoverflow.com/questions/2033150/subclassing-dict-should-dict-init-be-called)
        if data is None:
            pass
        elif isinstance(data, dict):
            for key in data:
                self.__setitem__(key, data[key])  # <==> self[key]=data[key]
                # x.__setitem__(i, y) <==> x[i]=y
        else:
            raise TypeError('expected dict')

    def __setitem__(self, key, value):
        if isinstance(value, dict) and not isinstance(value, DotDictify):  # TODO when would value have type DotDictify?
            value = DotDictify(value)
        elif isinstance(value, list):
            new_value = []
            if value:  # if value list is not empty
                if isinstance(value[0], dict):  # TODO can I assume that they will all be dicts if the first is?
                    for i in range(len(value)):  # DotDictify the items in the list
                        new_value.append(DotDictify(value[i]))
                    value = new_value
        super(DotDictify, self).__setitem__(key, value)  # calling dict's setitem

    def __getitem__(self, key):
        found = self.get(key, DotDictify.marker)
        # def get(self, k, d=None):
        #     D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None.
        if found is DotDictify.marker:  # TODO what does marker do here?
            found = DotDictify()
            super(DotDictify, self).__setitem__(key, found)  # TODO why set item here?
        return found

    __setattr__ = __setitem__
    __getattr__ = __getitem__

