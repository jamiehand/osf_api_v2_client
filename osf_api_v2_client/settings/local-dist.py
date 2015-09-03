"""
Example settings file. Copy this file to local.py and change
these settings.

Modify USER1, PASS1, USER2, and PASS2 to desired string values.
"""

from requests.auth import HTTPBasicAuth

DOMAIN = "https://staging2-api.osf.io/"  # TODO rename this variable?
API_PREFIX = "v2/"
URL = "{}{}".format(DOMAIN, API_PREFIX)  # e.g. https://staging2-api.osf.io/v2/

# Change these to the id's of nodes that were created by USER1.
PUBLIC_NODE_ID = 'pqbun'
PRIVATE_NODE_ID = 'vemxa'
FILES_NODE_ID = 'bc79a'  # public node with files to test file downloads

# Change these to the email and pw of the main user, who created
# the nodes
USER1 = ''
PASS1 = ''
AUTH1 = HTTPBasicAuth(USER1, PASS1)
USER1_ID = 'se6py'  # Jamie Hand

# Change these to the email and pw of a second user, who can't see
# the private node
USER2 = ''
PASS2 = ''
AUTH2 = HTTPBasicAuth(USER2, PASS2)
USER2_ID = 'cm98x'  # Jamie 2
