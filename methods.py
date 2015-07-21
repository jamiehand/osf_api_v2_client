import requests
import pprint

from requests.compat import urlparse, urlencode

# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth?

from requests.auth import HTTPBasicAuth

pp = pprint.PrettyPrinter()

def smart_print(string):
    try:
        print(string)
    except UnicodeEncodeError:
        print(string.encode('utf-8'))

# TODO could add "data" automatically if it doesn't say "links" (because
# "data" is the most common info to want)
# Instead of translating request into json request format, DotDictify transforms response itself.
# TODO seems like it would be more efficient to just translate the request as opposed to transforming the
# response ... unless we can transform the responses on a when-needed basis...?

# DocDictify class is modified from here:
# http://stackoverflow.com/questions/3031219/python-recursively-access-dict-via-attributes-as-well-as-index-access
class DotDictify(dict):
    marker = object()  # a new object  # TODO what does this do...?

    def __init__(self, data=None):
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
            if len(value) > 0:  # TODO or simply if value ?
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



class Iterator(object):
    def __init__(self, num_requested, url, cls, session, params=None, headers=None):
        # TODO allow num_requested of -1 to iterate over all of the items
        # If self.num_requested is None, all of the objects will be iterated
        # over. TODO or -1? (gh3 seems to use -1)
        self.num_requested = num_requested
        #: Number of items left in the iterator
        self.count = num_requested
        #: Current URL
        self.url = url
        #: Last URL that was requested
        self.last_url = url
        # TODO need this?
        self._api = self.url
        #: Class for constructing an item to return
        self.cls = cls
        #: Parameters of the query string
        self.params = params or {}
        # # TODO need this? What does it do?
        # self._remove_none(self.params)
        #: Headers generated for the GET request
        self.headers = headers or {}
        #: The last response seen
        self.last_response = None
        #: The last status code received
        self.last_status = 0

        self.path = urlparse(self.url).path

        #: JSON data on the page that was requested
        self.data = requests.get(self.url).json()[u'data']
        #: Navigation links on the page that was requested
        self.links = requests.get(self.url).json()[u'links']
        #: Number of items per page
        self.per_page = int(self.links[u'meta'][u'per_page'])
        #: Total items listed so far
        self.total_item_count = -1  # or 1 ?
        #: Number of the item on the page, for counting when to go onto the next page
        self.current_page_item_count = self.total_item_count % self.per_page

    # TODO better way to do this? Will this be fixed/not need to be updated once I write a general thing that parses
    # json and makes it more easily accessible?
    def update(self):
        self.data = requests.get(self.url).json()[u'data']  # TODO only needs to be done after page change
        #: Navigation links on the page that was requested
        self.links = requests.get(self.url).json()[u'links']  # TODO only needs to be done after page change
        #: Total items listed so far
        # self.total_item_count = 0  # or 1 ?  # TODO this is currently being updated within methods; change to be done here?
        # #: Number of items per page
        self.per_page = int(self.links[u'meta'][u'per_page'])  # TODO only needs to be done after page change
        #: Number of the item on the page, for counting when to go onto the next page
        self.current_page_item_count = self.total_item_count % self.per_page  # TODO needs to be done for every item?

    def _repr(self):
        return '<Iterator [{}, {}]>'.format(self.count, self.path)

    # TODO maybe use generator/yield statements to return these things more efficiently
    def next(self):  # Python 3: def __next__(self)
        # True when a 'next' link contains no value, i.e. there is no next page
        if self.url == None:
            raise StopIteration

        # Update the request data every time a new url is requested
        if self.last_url != self.url:
            self.update()
            self.last_url = self.url

        # Increment the item counts (total and per page)
        self.total_item_count += 1
        self.current_page_item_count = self.total_item_count % self.per_page

        # Only go up to the number requested
        if self.total_item_count >= self.num_requested:
            raise StopIteration()

        # If this is the last item in the page's data, return 'self' with the url of the next page
        if self.data[self.current_page_item_count] == self.data[-1]:
            self.url = self.links[u'next']  # go to the next page
            return self
        # Otherwise, return 'self' with the same url
        else:
            return self

    def __iter__(self):
        # reset values; e.g. self.cache_index = 0  # TODO more here?
        return self

# for node in Iterator(700, "https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 5, 5):
#     print node.url
#     print("{}. {}: {}".format(node.total_item_count + 1,
#                               node.data[node.current_page_item_count][u'provider'],
#                               node.data[node.current_page_item_count][u'name'].encode('utf-8')
#                               ))


# for node in Iterator(3, "https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 5, 5):
#     print("{}. {}: {}: {}".format(node.total_item_count,
#                               node.data[node.current_page_item_count][u'provider'],
#                               node.data[node.current_page_item_count][u'name'],
#                               node.data[node.current_page_item_count][u'links'][u'self']
#                              ))
#
# n = requests.get("https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive")
# data = n.json()[u'data']
# print("{}: {}: {}".format(data[0][u'provider'],
#                           data[0][u'name'],
#                           data[0][u'links'][u'self']
#                          ))
# print("{}: {}: {}".format(data[1][u'provider'],
#                           data[1][u'name'],
#                           data[1][u'links'][u'self']
#                          ))
#
# # TODO get "num_requested" working
# for node in Iterator(50, "https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 0, 0):
# #     print(node.data[node.total_item_count])
#     print(node)

    # def __iter__(self):
    #     self.last_url, params = self.url, self.params
    #     headers = self.headers
    #
    #     if 0 < self.count <= 100 and self.count != -1:
    #         params['per_page'] = self.count
    #
    #     if 'per_page' not in params and self.count == -1:
    #         params['per_page'] = 100
    #
    #     cls = self.cls
    #     # if issubclass(self.cls, models.GitHubCore):
    #     #     cls = functools.partial(self.cls, session=self)
    #
    #     while (self.count == -1 or self.count > 0) and self.last_url:
    #         response = self._get(self.last_url, params=params, headers=headers)
    #         self.last_response = response
    #         self.last_status = response.status_code
    #         if params:
    #             params = None  # rel_next already has the params TODO what is rel_next? the next page?
    #
    #         json = self._get_json(response)
    #
    #         if json is None:
    #             break
    #
    #         # languages returns a single dict. We want the items.
    #         if isinstance(json, dict):
    #             if issubclass(self.cls, models.GitHubObject):
    #                 raise exceptions.UnprocessableResponseBody(
    #                     "GitHub's API returned a body that could not be"
    #                     " handled", json
    #                 )
    #             if json.get('ETag'):
    #                 del json['ETag']
    #             if json.get('Last-Modified'):
    #                 del json['Last-Modified']
    #             json = json.items()
    #
    #         for i in json:
    #             yield cls(i)
    #             self.count -= 1 if self.count > 0 else 0
    #             if self.count == 0:
    #                 break
    #
    #         rel_next = response.links.get('next', {})
    #         self.last_url = rel_next.get('url', '')


# TODO should I make this class inside Session, or pass Session's url to the class when I instantiate a User object?
class User(object):
    """
    Represents an OSF user. This does not need to be the authenticated user for the Session; as long as the user_id
    is valid in the Session, a User object will be returned.
    There can be as many User objects as desired in a Session.
    """
    def __init__(self, user_id, url, auth=None):
        """
        :param user_id: 5-character user_id; must be a valid user_id in the current Session
        :param url: url of the Session in which this User object is being instantiated
        :param auth: optional authentication; same as auth of the current Session
        """
        # TODO should I assume that the user_id will be valid OR should I try/except to account for an invalid user_id
        # being passed in?
        self.response = requests.get('{}users/{}/'.format(url, user_id), auth=auth)
        self.data = DotDictify(self.response.json()[u'data'])
        # self.fullname = self.data[u'fullname']
        # self.given_name = self.data[u'given_name']
        # self.middle_name = self.data[u'middle_name']
        # self.family_name = self.data[u'family_name']
        # self.suffix = self.data[u'suffix']
        # self.gravatar_url = self.data[u'gravatar_url']
        # self.iter_emp_institutions = Iterator( num_requested=5)

    # TODO see if I can get this to work
    # def __getattr__(self, item):
    #     return self.data.item

class Session(object):
    def __init__(self, url='https://staging2.osf.io/api/v2/', auth=None):
        self.url = url
        self.auth = auth  # TODO is it okay to have auth be None?

    # TODO is this helpful? It is in the GitHub class of github3.py
    def me(self):
        """
        Retrieves info for the authenticated user in this Session object.
        :return: The representation of the authenticated user.
        """
        authenticated_user_id = 'abcd3'  # TODO how to get the user_id of the authenticated user?
        return requests.get('{}users/{}/'.format(self.url, authenticated_user_id))

    def root(self):
        """
        :return: the api root as designated by self.url
        """
        return requests.get(self.url)

    def user(self, user_id):
        """
        :param user_id: 5-character user id
        :return: the user identified by user_id
        """
        return User(user_id, self.url, auth=self.auth)

    def get_node_list(self):
        """
        :return: a list of nodes
        """
        node_list = requests.get('{}nodes/'.format(self.url), auth=self.auth)
        return node_list

    def get_node(self, node_id):
        """
        :param node_id: 5-character node id
        :return: the node identified by node_id
        """
        node = requests.get('{}nodes/{}/'.format(self.url, node_id), auth=self.auth)
        # TODO is the following better than the above? (the following was Reina's approach, by including the json.)
        # node = requests.get('{}nodes/{}/'.format(self.url, node_id), json={'node_id': node_id}, auth=self.auth)
        return node

    def create_node(self, title="", description="", category="", public="True"):
        """
        :param title: required, string
        :param description: optional, string
        :param category: optional, choice of '', 'project', 'hypothesis', 'methods and measures', 'procedure',
        'instrumentation', 'data', 'analysis', 'communication', 'other'
        :return: created node
        """
        params = {'title': title, 'description': description, 'category': category, 'public': public}
        node = requests.post('{}nodes/'.format(self.url), json=params, auth=self.auth)
        return node

    def edit_node(self, node_id, **kwargs):
        # Example kwargs: title='', description='', category='' TODO tags? public?
        # TODO how should this functionality work in terms of when a category is passed in or not?
        # TODO figure out how to change the private setting to public and vice versa
        params = {}  # 'node_id': node_id}
        for key, value in kwargs.iteritems():
            params[key] = value
        print params
        # TODO should this be PATCH or PUT? Should we have two diff. methods? It seems that PATCH
        # is more useful, because it seems pointless to require that the title be changed (which
        # PUT does, if I understand correctly).
        response = requests.patch('{}nodes/{}/'.format(self.url, node_id),
                                  json=params,
                                  # TODO should use json=params or data=params ?
                                  auth=self.auth
                                  )
        return response

    def delete_node(self, node_id):
        """
        :param node_id: 5-character node id
        :return: none
        """
        # params = {'node_id': node_id}
        # print('{}nodes/{}/'.format(self.url, node_id))
        response = requests.delete('{}nodes/{}/'.format(self.url, node_id), auth=self.auth)
        return response

