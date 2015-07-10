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
        node_list = requests.get('{}nodes/'.format(self.url, auth=self.auth))
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
        response = requests.delete('{}nodes/{}/'.format(self.url, node_id, auth=self.auth))
        return response



def main():
    print("\n \n ---------------------------------- STAGING2 ---------------------------------- \n \n")

    staging2_session = Session(user='user', pw='pass')
    print("staging2_session.url: {}".format(staging2_session.url))
    staging2_node = staging2_session.get_node('bxsu6')
    print(staging2_node.status_code)
    print("staging2_node.json():")
    pp.pprint(staging2_node.json())

    print("\n \n ---------------------------------- LOCALHOST:8000/v2/ ---------------------------------- \n \n")
    localhost_session = Session(domain="http://localhost:8000/", api_prefix="v2/",
                                user='user', pw='pass')
    print("localhost_session.url: {}".format(localhost_session.url))

    print("\n \n ---------------------------------- GET_ROOT() ---------------------------------- \n \n")
    root = localhost_session.get_root()
    pp.pprint(root.json())

    print("\n \n ------------------------------- GET_NODE(<public node id>) ------------------------------- \n \n")
    public_node = localhost_session.get_node('mrdnb')
    print("public_node.json(): ")
    pp.pprint(public_node.json())

    print("\n \n ------------------------------- GET_NODE(<private node id>) ------------------------------- \n \n")
    private_node = localhost_session.get_node('z9npx')
    print("private_node.json(): ")
    pp.pprint(private_node.json())

    print("\n \n ---------------------------------- CREATE_NODE(<private>) ---------------------------------- \n \n")
    created_private_node = localhost_session.create_node("Jamie's private node created with python")
    print("created_private_node.json(): ")
    pp.pprint(created_private_node.json())

    # print("\n \n ---------------------------------- CREATE_NODE(<public>) ---------------------------------- \n \n")
    # TODO how to create public node??
    # created_public_node = localhost_session.create_node("Creating public node with python 1", category="", public="true")
    # print("created_public_node.json(): ")
    # pp.pprint(created_public_node.json())

    print("\n \n ---------------------------------- EDIT_NODE(<private>) ---------------------------------- \n \n")

    print("\n \n ---------------------------------- EDIT_NODE(<public>) ---------------------------------- \n \n")

    print("\n \n ---------------------------------- DELETE_NODE(<private>) ---------------------------------- \n \n")

    print("\n \n ---------------------------------- DELETE_NODE(<public>) ---------------------------------- \n \n")

    # response4 = localhost_session.delete_node('x7s9m')
    # pp.pprint(private_node.content)
    # print(response4.status_code)

    # basic_auth = ('user', 'pass')
    # node_id = 'z9npx'
    # url = "http://localhost:8000/v2/nodes/{}/"
    #
    # res = requests.get(url.format(node_id), json={'node_id': node_id}, auth=basic_auth)
    # data = res.json()
    # pprint.pprint(data)

    # TODO get delete to work. It's giving a 204 response but not actually deleting the node. :(
    # see here: https://github.com/kennethreitz/requests/issues/1704

    # res = requests.delete(url.format(node_id), auth=basic_auth)
    # print("res.status_code: {}".format(res.status_code))

if __name__ == '__main__':
    main()
