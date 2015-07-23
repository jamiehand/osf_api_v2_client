import requests

from base.utils import DotDictify, response_generator


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

