import requests
import pprint

from requests.compat import urlparse, urlencode

# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth?

from requests.auth import HTTPBasicAuth

pp = pprint.PrettyPrinter()

class Iterator(object):
    def __init__(self, num_requested, url, cls, session, params=None, headers=None):
        # If self.num_requested is None, all of the objects will be iterated over. TODO or -1? (gh3 seems to use -1)
        self.num_requested = num_requested
        #: Number of items left in the iterator
        self.count = num_requested
        # TODO need this? : URL the class used to make its first GET
        self.url = url
        #: Last URL that was requested
        self.last_url = None
        # TODO need this?
        self._api = self.url
        #: Class for constructing an item to return
        self.cls = cls
        #: Parameters of the query string
        self.params = params or {}
        # TODO need this? What does it do?
        self._remove_none(self.params)
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
        #: Number of the item on the page, for counting when to go onto the next page
        self.item_number = 0  # or 1 ?

    def _repr(self):
        return '<Iterator [{}, {}]>'.format(self.count, self.path)

    def next(self):  # Python 3: def __next__(self)
        if self.links[u'next'] == 'null':  # or None ?  # if this is the last page
            if self.data[self.item_number] == self.data[-1]:  # if this is the last item in the page's data
                raise StopIteration()
            else:
                self.item_number += 1  # increment to go to the next item in the page's data
        else:  # if this is not the last page go to the next page
            if self.data[self.item_number] == self.data[-1]:  # if this is the last item in the page's data
                next_url = self.links[u'next']  # go to the next page
                # TODO how to pass in the next page needed?
            else:  # this is not the last item in the page's data
                self.item_number += 1  # go to the next item in the page's data

    def __iter__(self):
        # reset values; e.g. self.cache_index = 0
        return self

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
        self.data = self.response.json()[u'data']
        self.fullname = self.data[u'fullname']
        self.given_name = self.data[u'given_name']
        self.middle_name = self.data[u'middle_name']
        self.family_name = self.data[u'family_name']
        self.suffix = self.data[u'suffix']
        self.gravatar_url = self.data[u'gravatar_url']
        self.iter_emp_institutions = Iterator( num_requested=5)


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

