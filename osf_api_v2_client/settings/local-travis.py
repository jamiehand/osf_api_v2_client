"""
Example local settings file. Copy this file to local.py and change
these settings.

Modify USER1, PASS1, USER2, and PASS2 to desired string values.
"""

from requests.auth import HTTPBasicAuth

DOMAIN = "https://staging2.osf.io/"  # TODO rename this variable?
API_PREFIX = "api/v2/"
URL = "{}{}".format(DOMAIN, API_PREFIX)  # e.g. https://staging2.osf.io/api/v2/

# Change these to a public node id, and the id of a private node that
#  was created by USER1.
PUBLIC_NODE_ID = 'pqbun'
PRIVATE_NODE_ID = 'vemxa'

# Change these to the email and pw of the main user, who created the
# private node
USER1 = 'user1@example.com'
PASS1 = 'password1'
AUTH1 = HTTPBasicAuth(USER1, PASS1)
USER1_ID = 'se6py'  # Jamie Hand

# Change these to the email and pw of a second user, who can't see
# the private node
USER2 = 'user2@example.com'
PASS2 = 'password2'
AUTH2 = HTTPBasicAuth(USER2, PASS2)
USER2_ID = 'cm98x'  # Jamie 2
