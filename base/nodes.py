import requests

from base.utils import DotDictify, response_generator


class Node(DotDictify):
    """
    Represents an OSF node.
    There can be as many Node objects as desired in a Session.
    """
    def __init__(self, node_id, root_url, auth=None):
        """
        :param node_id: 5-character node_id; must be a valid node_id in the current Session
        :param root_url: root_url of the Session in which this Node object is being instantiated
        :param auth: optional authentication; same as auth of the current Session
        """
        self.url = '{}nodes/{}/'.format(root_url, node_id)
        self.response = requests.get(self.url, auth=auth)
        if self.response.status_code == 200:
            if u'data' in self.response.json():
                self.data = self.response.json()[u'data']
                super(Node, self).__init__(self.data)  # makes a DocDictify object out of response.json[u'data']
            else:
                raise ValueError("Invalid input for node_id: {}. Please provide a valid id for "
                                 "a node that you are authorized to view.".format(node_id))
        else:
            raise ValueError("Invalid input for node_id: {}. Please provide a valid id for "
                             "a node that you are authorized to view.".format(node_id))


