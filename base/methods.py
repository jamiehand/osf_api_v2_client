import requests

from base.utils import DotDictify, response_generator

# TODO create classes for: folders, files, contributors, node pointers, registrations, children, users/node lists, root?

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
        for key, value in kwargs.items():
            params[key] = value
        print(params)
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

