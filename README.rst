.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. .. image:: https://travis-ci.org/davidread/ckanext-rq.svg?branch=master
..     :target: https://travis-ci.org/davidread/ckanext-rq

.. .. image:: https://coveralls.io/repos/davidread/ckanext-rq/badge.svg
..   :target: https://coveralls.io/r/davidread/ckanext-rq

.. .. image:: https://pypip.in/download/ckanext-rq/badge.svg
..     :target: https://pypi.python.org/pypi//ckanext-rq/
..     :alt: Downloads

.. .. image:: https://pypip.in/version/ckanext-rq/badge.svg
..     :target: https://pypi.python.org/pypi/ckanext-rq/
..     :alt: Latest Version

.. .. image:: https://pypip.in/py_versions/ckanext-rq/badge.svg
..     :target: https://pypi.python.org/pypi/ckanext-rq/
..     :alt: Supported Python versions

.. .. image:: https://pypip.in/status/ckanext-rq/badge.svg
..     :target: https://pypi.python.org/pypi/ckanext-rq/
..     :alt: Development Status

.. .. image:: https://pypip.in/license/ckanext-rq/badge.svg
..     :target: https://pypi.python.org/pypi/ckanext-rq/
..     :alt: License

=============
ckanext-rq
=============

This is a backport of the RQ-based background jobs code seen in CKAN 2.7, to
enable earlier versions of CKAN to run rq-based background tasks.

It is based on the code by @torfsen, mainly here: https://github.com/ckan/ckan/pull/3165

TODO:

* check Redis is available on startup
* setting ckan.redis.url from environment variable CKAN_REDIS_URL
* transfer the tests and RQTestBase

----
Note
----

You won't be able to use the normal plugin.toolkit.enqueue_job function. Use
this import which contains a fallback::

    try:
        enqueue_job = p.toolkit.enqueue_job
    except AttributeError:
        from ckanext.rq.jobs import enqueue as enqueue_job

------------
Requirements
------------

For CKAN versions 2.3 to 2.6.x. (Must not be used with CKAN 2.7.0 or later)

------------
Installation
------------

You need Redis installed::

    sudo apt-get install redis-server

To install ckanext-rq:

1. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

2. Install the ckanext-rq Python package into your virtual environment::

..     pip install ckanext-rq
     pip install git+https://github.com/davidread/ckanext-rq.git

.. 3. Add ``rq`` to the ``ckan.plugins`` setting in your CKAN
..    config file (by default the config file is located at
..    ``/etc/ckan/default/production.ini``).

3. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload

4. Start the worker::

     paster --plugin=ckanext-rq jobs worker --config=/etc/ckan/default/development.ini

5. To run the worker in a robust way, install and configure Supervisor: http://docs.ckan.org/en/latest/maintaining/background-tasks.html#using-supervisor

---------------
Config Settings
---------------

::

    # URL to your Redis instance, including the database to be used.
    ckan.redis.url = redis://localhost:6379/0


.. ------------------------
.. Development Installation
.. ------------------------

.. To install ckanext-rq for development, activate your CKAN virtualenv and
.. do:

..     git clone https://github.com/davidread/ckanext-rq.git
..     cd ckanext-rq
..     python setup.py develop
..     pip install -r dev-requirements.txt


.. -----------------
.. Running the Tests
.. -----------------

.. To run the tests, do::

..     nosetests --nologcapture --with-pylons=test.ini

.. To run the tests and produce a coverage report, first make sure you have
.. coverage installed in your virtualenv (``pip install coverage``) then run::

..     nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.rq --cover-inclusive --cover-erase --cover-tests


.. ---------------------------------
.. Registering ckanext-rq on PyPI
.. ---------------------------------

.. ckanext-rq should be availabe on PyPI as
.. https://pypi.python.org/pypi/ckanext-rq. If that link doesn't work, then
.. you can register the project on PyPI for the first time by following these
.. steps:

.. 1. Create a source distribution of the project::

..      python setup.py sdist

.. 2. Register the project::

..      python setup.py register

.. 3. Upload the source distribution to PyPI::

..      python setup.py sdist upload

.. 4. Tag the first release of the project on GitHub with the version number from
..    the ``setup.py`` file. For example if the version number in ``setup.py`` is
..    0.0.1 then do::

..        git tag 0.0.1
..        git push --tags


.. ----------------------------------------
.. Releasing a New Version of ckanext-rq
.. ----------------------------------------

.. ckanext-rq is availabe on PyPI as https://pypi.python.org/pypi/ckanext-rq.
.. To publish a new version to PyPI follow these steps:

.. 1. Update the version number in the ``setup.py`` file.
..    See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
..    for how to choose version numbers.

.. 2. Create a source distribution of the new version::

..      python setup.py sdist

.. 3. Upload the source distribution to PyPI::

..      python setup.py sdist upload

.. 4. Tag the new release of the project on GitHub with the version number from
..    the ``setup.py`` file. For example if the version number in ``setup.py`` is
..    0.0.2 then do::

..        git tag 0.0.2
..        git push --tags
