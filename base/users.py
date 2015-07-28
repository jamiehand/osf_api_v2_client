import requests

from base.utils import DotDictify, response_generator


class User(DotDictify):
    """
    Represents an OSF user. This does not need to be the authenticated user for the
    Session; as long as the user_id is valid in the Session, a User object will be returned.
    There can be as many User objects as desired in a Session.
    """
    def __init__(self, user_id, root_url, auth=None):
        # TODO what should happen if someone requests a nonexistent user? should I assume that the user_id will
        # be valid OR should I try/except to account for an invalid user_id being passed in?
        """
        :param user_id: 5-character user_id; must be a valid user_id in the current Session
        :param root_url: root_url of the Session in which this User object is being instantiated
        :param auth: optional authentication; same as auth of the current Session
        """
        self.response = requests.get('{}users/{}/'.format(root_url, user_id), auth=auth)
        self.data = self.response.json()[u'data']
        super(User, self).__init__(self.data)  # makes a DocDictify object out of response.json[u'data']

