import requests
import pprint

# TODO import API_PREFIX? (also, import domain?)
# TODO change auth to work with OAuth/tokens instead of basic auth?

from requests.auth import HTTPBasicAuth

pp = pprint.PrettyPrinter()

class Session(object):
    def __init__(self, domain='https://staging2.osf.io/', api_prefix='api/v2/', user='', pw=''):
        self.domain = domain  # TODO use 'or' for giving optional parameter?
        self.api_prefix = api_prefix
        self.url = '{}{}'.format(self.domain, self.api_prefix)
        # self.auth = HTTPBasicAuth(user, pw) TODO is this line not better than the line below?
        if user == '':  # TODO also include "or (pw == '')" ?
            self.auth = None  # TODO check if setting this to None is a valid fix. It seems to work! But I'm not
                              # sure what's going on behind the scenes.
        else:
            self.auth = (user, pw)

    def get_root(self):
        """
        :return: the api root as designated by self.url
        """
        return requests.get(self.url)

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

