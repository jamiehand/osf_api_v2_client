import requests

from osf_api_v2_client.utils import DotDictify, response_generator, get_response_or_exception


class User(DotDictify):
    """
    Represents an OSF user. This does not need to be the authenticated user for the
    Session; as long as the user_id is valid in the Session, a User object will be returned.
    There can be as many User objects as desired in a Session.
    """
    def __init__(self, user_id, root_url, auth=None):
        """
        :param user_id: 5-character user_id; must be a valid user_id in the current Session
        :param root_url: root_url of the Session in which this User object is being instantiated
        :param auth: optional authentication; same as auth of the current Session
        """
        self.url = '{}users/{}/'.format(root_url, user_id)
        self.response = get_response_or_exception(self.url, auth=auth)
        self.data = self.response.json()[u'data']
        super(User, self).__init__(self.data)  # makes a DocDictify object out of response.json[u'data']

