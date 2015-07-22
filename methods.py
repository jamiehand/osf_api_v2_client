import requests
import pprint

from requests.compat import urlparse, urlencode

from requests.auth import HTTPBasicAuth

pp = pprint.PrettyPrinter()

def smart_print(string):
    try:
        print(string)
    except UnicodeEncodeError:
        print(string.encode('utf-8'))

# Instead of translating request into json request format, DotDictify transforms response itself.
# TODO seems like it would be more efficient to just translate the request as opposed to transforming the
# response ... unless we can transform the responses on a when-needed basis...?
# DocDictify class is modified from here:
# http://stackoverflow.com/questions/3031219/python-recursively-access-dict-via-attributes-as-well-as-index-access
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


# for node in Iterator(700, "https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 5, 5):
#     print node.url
#     print("{}. {}: {}".format(node.total_item_count + 1,
#                               node.data[node.current_page_item_count][u'provider'],
#                               node.data[node.current_page_item_count][u'name'].encode('utf-8')
#                               ))


# for node in Iterator(3, "https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 5, 5):
#     # print("{}. {}: {}: {}".format(node.total_item_count,
#     #                           node[u'provider'],
#     #                           node[u'name'],
#     #                           node[u'links'][u'self']
#     #                          ))
#     print(1)

def generator_function(url, num_requested=-1):
    """
    :param num_requested: the number of items desired; if -1, all items available will be returned
    :param url: the url where the desired items are located
    :return: a generator of the items desired
    """
    #: Number of items left in the generator
    count_remaining = num_requested
    #: Next url to get the json response from
    url = url

    print(url)
    while url is not None:
        json_response = requests.get(url).json()
        print(json_response)
        for item in json_response[u'data']:
            if count_remaining > 0 or num_requested == -1:
                count_remaining -= 1
                print("count_remaining: {}".format(count_remaining))
                yield item
        url = json_response[u'links'][u'next']

# happy_gen = generator_function("https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 4)
# for item in happy_gen:
#     print item

big_gen = generator_function("https://staging2.osf.io/api/v2/users/se6py/nodes/")
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())
print(big_gen.next())

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
# for node in Iterator(50, "https://staging2.osf.io/api/v2/nodes/xtf45/files/?path=%2F&provider=googledrive", 0, 0):
# #     print(node.data[node.total_item_count])
#     print(node)


class User(DotDictify):
    """
    Represents an OSF user. This does not need to be the authenticated user for the Session; as long as the user_id
    is valid in the Session, a User object will be returned.
    There can be as many User objects as desired in a Session.
    """
    def __init__(self, user_id, url, auth=None):
        # TODO what should happen if someone requests a nonexistent user? should I assume that the user_id will
        # be valid OR should I try/except to account for an invalid user_id being passed in?
        """
        :param user_id: 5-character user_id; must be a valid user_id in the current Session
        :param url: url of the Session in which this User object is being instantiated
        :param auth: optional authentication; same as auth of the current Session
        """
        self.response = requests.get('{}users/{}/'.format(url, user_id), auth=auth)
        self.data = self.response.json()[u'data']
        super(User, self).__init__(self.data)  # makes a DocDictify object out of response.json[u'data']


class Node(DotDictify):
    """
    Represents an OSF node.
    There can be as many Node objects as desired in a Session.
    """
    def __init__(self, node_id, url, auth=None):
        # TODO what should happen if someone requests a node that is not visible to them? or a nonexistent node?
        """
        :param node_id: 5-character node_id; must be a valid node_id in the current Session
        :param url: url of the Session in which this Node object is being instantiated
        :param auth: optional authentication; same as auth of the current Session
        """
        self.response = requests.get('{}nodes/{}/'.format(url, node_id), auth=auth)
        self.data = self.response.json()[u'data']
        super(Node, self).__init__(self.data)  # makes a DocDictify object out of response.json[u'data']

# TODO create classes for any/all of folders, files, contributors, node pointers, registrations, (children) ?

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

