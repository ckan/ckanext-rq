import collections
import contextlib
import logging
import re

import rq
from ckantoolkit import config
from ckantoolkit.tests.helpers import FunctionalTestBase

from ckan import logic

from ckanext.rq.redis import connect_to_redis

import ckanext.rq.jobs as jobs


@contextlib.contextmanager
def changed_config(key, value):
    '''
    Context manager for temporarily changing a config value.

    Allows you to temporarily change the value of a CKAN configuration
    option. The original value is restored once the context manager is
    left.

    Usage::

        with changed_config(u'ckan.site_title', u'My Test CKAN'):
            assert config[u'ckan.site_title'] == u'My Test CKAN'

    .. seealso:: The decorator :py:func:`change_config`
    '''
    _original_config = config.copy()
    config[key] = value
    try:
        yield
    finally:
        config.clear()
        config.update(_original_config)


class RQTestBase(object):
    '''
    Base class for tests of RQ functionality.
    '''
    def setup(self):
        u'''
        Delete all RQ queues and jobs.
        '''
        # See https://github.com/nvie/rq/issues/731
        redis_conn = connect_to_redis()
        for queue in rq.Queue.all(connection=redis_conn):
            queue.empty()
            redis_conn.srem(rq.Queue.redis_queues_keys, queue._key)
            redis_conn.delete(queue._key)

    def all_jobs(self):
        u'''
        Get a list of all RQ jobs.
        '''
        jobs = []
        redis_conn = connect_to_redis()
        for queue in rq.Queue.all(connection=redis_conn):
            jobs.extend(queue.jobs)
        return jobs

    def enqueue(self, job=None, *args, **kwargs):
        u'''
        Enqueue a test job.
        '''
        if job is None:
            job = jobs.test_job
        return jobs.enqueue(job, *args, **kwargs)


class FunctionalRQTestBase(FunctionalTestBase, RQTestBase):
    '''
    Base class for functional tests of RQ functionality.
    '''
    def setup(self):
        FunctionalTestBase.setup(self)
        RQTestBase.setup(self)


@contextlib.contextmanager
def recorded_logs(logger=None, level=logging.DEBUG,
                  override_disabled=True, override_global_level=True):
    u'''
    Context manager for recording log messages.

    :param logger: The logger to record messages from. Can either be a
        :py:class:`logging.Logger` instance or a string with the
        logger's name. Defaults to the root logger.

    :param int level: Temporary log level for the target logger while
        the context manager is active. Pass ``None`` if you don't want
        the level to be changed. The level is automatically reset to its
        original value when the context manager is left.

    :param bool override_disabled: A logger can be disabled by setting
        its ``disabled`` attribute. By default, this context manager
        sets that attribute to ``False`` at the beginning of its
        execution and resets it when the context manager is left. Set
        ``override_disabled`` to ``False`` to keep the current value
        of the attribute.

    :param bool override_global_level: The ``logging.disable`` function
        allows one to install a global minimum log level that takes
        precedence over a logger's own level. By default, this context
        manager makes sure that the global limit is at most ``level``,
        and reduces it if necessary during its execution. Set
        ``override_global_level`` to ``False`` to keep the global limit.

    :returns: A recording log handler that listens to ``logger`` during
        the execution of the context manager.
    :rtype: :py:class:`RecordingLogHandler`

    Example::

        import logging

        logger = logging.getLogger(__name__)

        with recorded_logs(logger) as logs:
            logger.info(u'Hello, world!')

        logs.assert_log(u'info', u'world')
    '''
    if logger is None:
        logger = logging.getLogger()
    elif not isinstance(logger, logging.Logger):
        logger = logging.getLogger(logger)
    handler = RecordingLogHandler()
    old_level = logger.level
    manager_level = logger.manager.disable
    disabled = logger.disabled
    logger.addHandler(handler)
    try:
        if level is not None:
            logger.setLevel(level)
        if override_disabled:
            logger.disabled = False
        if override_global_level:
            if (level is None) and (manager_level > old_level):
                logger.manager.disable = old_level
            elif (level is not None) and (manager_level > level):
                logger.manager.disable = level
        yield handler
    finally:
        logger.handlers.remove(handler)
        logger.setLevel(old_level)
        logger.disabled = disabled
        logger.manager.disable = manager_level


class RecordingLogHandler(logging.Handler):
    u'''
    Log handler that records log messages for later inspection.

    You can inspect the recorded messages via the ``messages`` attribute
    (a dict that maps log levels to lists of messages) or by using
    ``assert_log``.

    This class is rarely useful on its own, instead use
    :py:func:`recorded_logs` to temporarily record log messages.
    '''
    def __init__(self, *args, **kwargs):
        super(RecordingLogHandler, self).__init__(*args, **kwargs)
        self.clear()

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())

    def assert_log(self, level, pattern, msg=None):
        u'''
        Assert that a certain message has been logged.

        :param string pattern: A regex which the message has to match.
            The match is done using ``re.search``.

        :param string level: The message level (``'debug'``, ...).

        :param string msg: Optional failure message in case the expected
            log message was not logged.

        :raises AssertionError: If the expected message was not logged.
        '''
        compiled_pattern = re.compile(pattern)
        for log_msg in self.messages[level]:
            if compiled_pattern.search(log_msg):
                return
        if not msg:
            if self.messages[level]:
                lines = u'\n    '.join(self.messages[level])
                msg = (u'Pattern "{}" was not found in the log messages for '
                       + u'level "{}":\n    {}').format(pattern, level, lines)
            else:
                msg = (u'Pattern "{}" was not found in the log messages for '
                       + u'level "{}" (no messages were recorded for that '
                       + u'level).').format(pattern, level)
        raise AssertionError(msg)

    def clear(self):
        u'''
        Clear all captured log messages.
        '''
        self.messages = collections.defaultdict(list)


def call_action(action_name, context=None, **kwargs):
    '''Call the named ``ckan.logic.action`` function and return the result.

    This is just a nicer way for user code to call action functions, nicer than
    either calling the action function directly or via
    :py:func:`ckan.logic.get_action`.

    For example::

        user_dict = call_action('user_create', name='seanh',
                                email='seanh@seanh.com', password='pass')

    Any keyword arguments given will be wrapped in a dict and passed to the
    action function as its ``data_dict`` argument.

    Note: this skips authorization! It passes 'ignore_auth': True to action
    functions in their ``context`` dicts, so the corresponding authorization
    functions will not be run.
    This is because ckan.tests.logic.action tests only the actions, the
    authorization functions are tested separately in
    ckan.tests.logic.auth.
    See the :doc:`testing guidelines </contributing/testing>` for more info.

    This function should eventually be moved to
    :py:func:`ckan.logic.call_action` and the current
    :py:func:`ckan.logic.get_action` function should be
    deprecated. The tests may still need their own wrapper function for
    :py:func:`ckan.logic.call_action`, e.g. to insert ``'ignore_auth': True``
    into the ``context`` dict.

    :param action_name: the name of the action function to call, e.g.
        ``'user_update'``
    :type action_name: string
    :param context: the context dict to pass to the action function
        (optional, if no context is given a default one will be supplied)
    :type context: dict
    :returns: the dict or other value that the action function returns

    '''
    if context is None:
        context = {}
    context.setdefault('user', '127.0.0.1')
    context.setdefault('ignore_auth', True)
    return logic.get_action(action_name)(context=context, data_dict=kwargs)
