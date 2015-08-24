=================
osf_api_v2_client
=================

.. image:: https://img.shields.io/travis/jamiehand/osf_api_v2_client.svg
        :target: https://travis-ci.org/jamiehand/osf_api_v2_client

.. TODO:: this, once on PyPI
.. .. image:: https://img.shields.io/pypi/v/osf_api_v2_client.svg
        :target: https://pypi.python.org/pypi/osf_api_v2_client


A client for accessing the OSF v2 API

* Free software: Apache license
* Documentation: https://osf-api-v2-client.readthedocs.org.

Features
--------

* Simplifies access of JSON dictionary (dict) data:

    - Instead of ``user[u'attributes'][u'fullname']``,
      ``user.attributes.fullname`` can be used.

    - However, you are not locked into the simplified "dot" access.
      Both regular dict access and "dot" access will work, and they
      can be switched up::

        user[u'attributes'].fullname
        user.attributes[u'fullname']

    - This works recursively for dicts within dicts
      (as seen above, given

      ``user = {u'attributes':
      {u'fullname': u'John Cleese'}}``),

      and for dicts inside a list of dicts (see below).

    - Given::

            dict_with_list = {
                u'mylist': [
                    {u'fullname': u'John Cleese'},
                    {u'fullname': u'Terry Jones'},
                    {u'fullname': u'Eric Idle'}
                ]
            }

    - Calls such as the following can be used::

            dict_with_list.mylist[0].fullname
            dict_with_list[u'mylist'][2][u'fullname']

* Simplifies access of multiple items:

    - Though items are returned from the API with only a certain number
      of items per page (often ten), this library takes care of pagination
      in the background, providing a generator to return all desired items
      one at a time within a loop.

    - The following example prints the gravatar
      urls of the first 30 users in the OSF::

          from osf_api_v2_client.session import Session

          session = Session()
          for user in session.get_user_generator(num_requested=30):
              print(user.attributes.gravatar_url)

