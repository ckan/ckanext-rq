# encoding: utf-8

import logging
import ckan.lib.navl.dictization_functions
import ckan.logic as logic
import ckan.plugins as p

from ckanext.rq import jobs
from ckanext.rq import schema

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust
_validate = ckan.logic.validate
_check_access = p.toolkit.check_access
NotFound = p.toolkit.ObjectNotFound


@_validate(schema.job_list_schema)
def job_list(context, data_dict):
    '''List enqueued background jobs.

    :param list queues: Queues to list jobs from. If not given then the
        jobs from all queues are listed.

    :returns: The currently enqueued background jobs.
    :rtype: list

    .. versionadded:: 2.7
    '''
    _check_access(u'job_list', context, data_dict)
    dictized_jobs = []
    queues = data_dict.get(u'queues')
    if queues:
        queues = [jobs.get_queue(q) for q in queues]
    else:
        queues = jobs.get_all_queues()
    for queue in queues:
        for job in queue.jobs:
            dictized_jobs.append(jobs.dictize_job(job))
    return dictized_jobs


def job_show(context, data_dict):
    '''Show details for a background job.

    :param string id: The ID of the background job.

    :returns: Details about the background job.
    :rtype: dict

    .. versionadded:: 2.7
    '''
    _check_access(u'job_show', context, data_dict)
    id = _get_or_bust(data_dict, u'id')
    try:
        return jobs.dictize_job(jobs.job_from_id(id))
    except KeyError:
        raise NotFound


@_validate(schema.job_clear_schema)
def job_clear(context, data_dict):
    '''Clear background job queues.

    Does not affect jobs that are already being processed.

    :param list queues: The queues to clear. If not given then ALL
        queues are cleared.

    :returns: The cleared queues.
    :rtype: list

    .. versionadded:: 2.7
    '''
    _check_access(u'job_clear', context, data_dict)
    queues = data_dict.get(u'queues')
    if queues:
        queues = [jobs.get_queue(q) for q in queues]
    else:
        queues = jobs.get_all_queues()
    names = [jobs.remove_queue_name_prefix(queue.name) for queue in queues]
    for queue, name in zip(queues, names):
        queue.empty()
        log.info(u'Cleared background job queue "{}"'.format(name))
    return names


def job_cancel(context, data_dict):
    '''Cancel a queued background job.

    Removes the job from the queue and deletes it.

    :param string id: The ID of the background job.

    .. versionadded:: 2.7
    '''
    _check_access(u'job_cancel', context, data_dict)
    id = _get_or_bust(data_dict, u'id')
    try:
        jobs.job_from_id(id).delete()
        log.info(u'Cancelled background job {}'.format(id))
    except KeyError:
        raise NotFound
