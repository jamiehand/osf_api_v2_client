import requests

from osf_api_v2_client.utils import(DotNotator,
                                    dotnotator_generator,
                                    json_dict_generator,
                                    file_generator,
                                    get_response_or_exception)


class Session(object):
    def __init__(self, root_url='https://staging2.osf.io/api/v2/', auth=None):
        self.root_url = root_url
        self.auth = auth

    def get_root(self):
        """
        :return: a DotNotator object of the api root as designated
        by self.root_url
        """
        response = get_response_or_exception('get', self.root_url)
        response_json = response.json()
        return DotNotator(response_json)

    # USER ACTIONS

    def get_user_generator(self, num_requested=-1):
        """
        :param num_requested: a positive integer or -1; -1 will cause
        all users to be returned; otherwise num_requested number of
        users will be returned
        :return: a generator containing users
        """
        target_url = '{}users/'.format(self.root_url)
        return dotnotator_generator(target_url, auth=self.auth,
                                    num_requested=num_requested)

    def get_user(self, user_id):
        """
        :param user_id: 5-character user id
        :return: the user identified by user_id
        """
        url = '{}users/{}/'.format(self.root_url, user_id)
        response = get_response_or_exception('get', url, auth=self.auth)
        data = response.json()[u'data']
        return DotNotator(data)

    # NODE ACTIONS

    def get_node_generator(self, num_requested=-1):
        """
        :param num_requested: a positive integer or -1; -1 will cause
        all nodes to be returned; otherwise num_requested number of
        nodes will be returned
        :return: a generator containing nodes
        """
        target_url = '{}nodes/'.format(self.root_url)
        return dotnotator_generator(target_url, auth=self.auth,
                                    num_requested=num_requested)

    def get_node(self, node_id=''):
        """
        :param node_id: 5-character id for a node that can be
        viewed by this session's auth
        :return: the node identified by node_id
        """
        url = '{}nodes/{}/'.format(self.root_url, node_id)
        response = get_response_or_exception('get', url, auth=self.auth)
        data = response.json()[u'data']
        return DotNotator(data)

    def create_node(self, title, description="",
                    category=""):
        """
        :param title: required, string
        :param description: optional, string
        :param category: optional, choice of '', 'project',
        'hypothesis', 'methods and measures', 'procedure',
        'instrumentation', 'data', 'analysis', 'communication',
        'other'
        :return: DotNotator version of created node
        """
        # TODO once functionality exists to create public nodes w/ API,
        # add 'public' bool to create_node parameters, and add the
        # functionality in this method.
        params = {'title': title, 'description': description,
                  'category': category}
        node = get_response_or_exception(
            'post', '{}nodes/'.format(self.root_url),
            json=params, auth=self.auth
        )
        node_json = node.json()[u'data']
        return DotNotator(node_json)

    def edit_node(self, node_id, **kwargs):
        """
        :param node_id: 5-character id for a node that can be
        edited by this session's auth
        :param kwargs: e.g. title='My Title',
        description='This is my new description',
        category='data'
        :return: DotNotator version of edited node
        """
        # e.g. kwargs: title='', description='', category=''
        params = {}
        for key, value in kwargs.items():
            params[key] = value
        edited_node = get_response_or_exception(
            'patch', '{}nodes/{}/'.format(self.root_url, node_id),
            json=params,
            auth=self.auth
        )
        edited_node_json = edited_node.json()[u'data']
        return DotNotator(edited_node_json)

    def delete_node(self, node_id):
        """
        :param node_id: 5-character node id
        :return: none
        """
        get_response_or_exception(
            'delete', '{}nodes/{}/'.format(self.root_url, node_id),
            auth=self.auth
        )

    # FILE ACTIONS

    def get_file_generator(self, node_id, num_requested=-1):
        """
        :param node_id: 5-character node id
        :param num_requested: a positive integer or -1;
        -1 will cause all files to be returned;
        otherwise num_requested number of files will be returned
        :return: a generator containing files related to node_id
        """
        node = self.get_node(node_id)
        files_url = node.links.files.related
        return file_generator(files_url, auth=self.auth)
