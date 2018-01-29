=============
ckanext-rq
=============

Background jobs functionality for CKAN 2.6 and earlier.

This is a backport of the new `background jobs functionality
<http://docs.ckan.org/en/latest/maintaining/background-tasks.html>`_ introduced
in CKAN 2.7. With this extension, you can make use of that system in earlier
versions of CKAN.

It is based on `code by @torfsen <https://github.com/ckan/ckan/pull/3165>`_.


------------
Requirements
------------

For CKAN versions 2.3 to 2.6.x. (Must not be used with CKAN 2.7.0 or later)

You need Redis installed::

    sudo apt-get install redis-server


------------
Installation
------------

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-rq Python package into your virtual environment::

    pip install -e git+https://github.com/ckan/ckanext-rq.git

3. Install the necessary dependencies::

    pip install -r /usr/lib/ckan/default/src/ckanext-rq/requirements.txt

4. Add ``rq`` to the list of plugins your CKAN configuration file (by default
   ``/etc/ckan/default/production.ini``)::

    ckan.plugins = ... rq

5. Start a worker (to run the worker in a robust way, install and configure Supervisor: http://docs.ckan.org/en/latest/maintaining/background-tasks.html#using-supervisor)::

    paster --plugin=ckanext-rq jobs worker --config=/etc/ckan/default/production.ini

6. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


-----
Usage
-----

You won't be able to use the normal ``plugin.toolkit.enqueue_job`` function.
Use this import which contains a fallback::

    from ckan.plugins import toolkit
    try:
        enqueue_job = toolkit.enqueue_job
    except AttributeError:
        from ckanext.rq.jobs import enqueue as enqueue_job


---------------
Config Settings
---------------

::

    # URL to your Redis instance, including the database to be used.
    ckan.redis.url = redis://localhost:6379/0


-----------
Open Issues
-----------

- Check that Redis is available on startup

- Support for setting ``ckan.redis.url`` from the environment variable
  ``CKAN_REDIS_URL``


------------------------
Development Installation
------------------------

To install ckanext-rq for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/ckan/ckanext-rq.git
    cd ckanext-rq
    python setup.py develop
    pip install -r requirements.txt
    pip install -r dev-requirements.txt

You also need to install Redis, activate the plugin in your CKAN configuration and run a worker as described above.

-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.rq --cover-inclusive --cover-erase --cover-tests

