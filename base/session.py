import requests
from urllib.parse import urljoin

from base.utils import DotDictify, response_generator
from base.users import User
from base.nodes import Node

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

    def nodes(self, node_id='', num_requested=-1):
        # TODO try/except error of invalid node_id?
        # TODO what about permissions?
        """
        If node_id is None, return a generator containing nodes
        If node_id is a valid id, return the node with that id
        If node_id is not a valid node id, raise exception
        :param node_id: 5-character node id
        :param num_requested: a positive integer or -1; -1 will cause all nodes
        to be returned; otherwise num_requested number of nodes will be returned
        :return: the node identified by node_id , or a generator containing nodes
        """
        # if not node_id:  # TODO or, if node_id could be anything but a string: if node_id == ''
            # get all the nodes

            # node_gen = response_generator('{}nodes/'.format(self.url), auth=self.auth, num_requested=num_requested)
            # return node_gen
            # node_list = requests.get('{}nodes/'.format(self.url), auth=self.auth)
        # elif isinstance(node_id, str):
        #     # get the one node
        #     # try:
        #     node = requests.get('{}nodes/{}/'.format(self.url, node_id), auth=self.auth)
        #     return node
        #     # except (invalid node id):
        #     #     # TODO raise exception? specify which exception in docstring if so!
        #     #     pass
        # if not node_id:  # TODO or, if node_id could be anything but a string: if node_id == ''
        node_id_string = '{}/'.format(node_id).lstrip('/')  # if node_id is empty, remove '/' to
                                                            # avoid interpretation as absolute path
        target_url = urljoin('{}nodes/'.format(self.url), node_id_string)
        print(target_url)
        response = requests.get(target_url, auth=self.auth)
        print(response.json())
        if u'data' in response.json():
            response_data = response.json()[u'data']
            if isinstance(response_data, list):  # if data is a list (node list), return iterator of data
                return response_generator(target_url, auth=self.auth)  # TODO: inefficient? Makes 1st GET request twice
            elif isinstance(response_data, dict):  # elif data is a dict (single node), return DotDictify of data
                return DotDictify(response_data)
            else:
                raise ValueError("Invalid input for node_id: {}. Please leave node_id blank to get node generator, or "
                                 "provide a valid id for a node that you are authorized to view.".format(node_id))
        else:
            raise ValueError("Invalid input for node_id: {}. Please leave node_id blank to get node generator, or "
                             "provide a valid id for a node that you are authorized to view.".format(node_id))

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
