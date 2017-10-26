import re
import nose
import datetime

from nose.tools import eq_ as eq, ok_ as ok, assert_raises, raises

from ckantoolkit import ObjectNotFound
from ckantoolkit.tests import helpers
try:
    from ckan.tests.helpers import call_action
except ImportError:
    from ckanext.rq.tests.helpers import call_action

from ckanext.rq.tests.helpers import FunctionalRQTestBase, recorded_logs
from ckanext.rq import jobs


class TestJobList(FunctionalRQTestBase):

    def test_all_queues(self):
        '''
        Test getting jobs from all queues.
        '''
        job1 = self.enqueue()
        job2 = self.enqueue()
        job3 = self.enqueue(queue=u'my_queue')
        jobs = call_action(u'job_list')
        eq(len(jobs), 3)
        eq({job[u'id'] for job in jobs}, {job1.id, job2.id, job3.id})

    def test_specific_queues(self):
        '''
        Test getting jobs from specific queues.
        '''
        job1 = self.enqueue()
        job2 = self.enqueue(queue=u'q2')
        job3 = self.enqueue(queue=u'q3')
        job4 = self.enqueue(queue=u'q3')
        jobs = call_action(u'job_list', queues=[u'q2'])
        eq(len(jobs), 1)
        eq(jobs[0][u'id'], job2.id)
        jobs = call_action(u'job_list', queues=[u'q2', u'q3'])
        eq(len(jobs), 3)
        eq({job[u'id'] for job in jobs}, {job2.id, job3.id, job4.id})


class TestJobShow(FunctionalRQTestBase):

    def test_existing_job(self):
        '''
        Test showing an existing job.
        '''
        job = self.enqueue(queue=u'my_queue', title=u'Title')
        d = call_action(u'job_show', id=job.id)
        eq(d[u'id'], job.id)
        eq(d[u'title'], u'Title')
        eq(d[u'queue'], u'my_queue')
        dt = datetime.datetime.strptime(d[u'created'], u'%Y-%m-%dT%H:%M:%S')
        now = datetime.datetime.utcnow()
        ok(abs((now - dt).total_seconds()) < 10)

    @nose.tools.raises(ObjectNotFound)
    def test_not_existing_job(self):
        '''
        Test showing a not existing job.
        '''
        call_action(u'job_show', id=u'does-not-exist')


class TestJobClear(FunctionalRQTestBase):

    def test_all_queues(self):
        '''
        Test clearing all queues.
        '''
        self.enqueue()
        self.enqueue(queue=u'q')
        self.enqueue(queue=u'q')
        self.enqueue(queue=u'q')
        queues = call_action(u'job_clear')
        eq({jobs.DEFAULT_QUEUE_NAME, u'q'}, set(queues))
        all_jobs = self.all_jobs()
        eq(len(all_jobs), 0)

    def test_specific_queues(self):
        '''
        Test clearing specific queues.
        '''
        job1 = self.enqueue()
        job2 = self.enqueue(queue=u'q1')
        job3 = self.enqueue(queue=u'q1')
        job4 = self.enqueue(queue=u'q2')
        with recorded_logs(u'ckanext.rq.action') as logs:
            queues = call_action(u'job_clear', queues=[u'q1', u'q2'])
        eq({u'q1', u'q2'}, set(queues))
        all_jobs = self.all_jobs()
        eq(len(all_jobs), 1)
        eq(all_jobs[0], job1)
        logs.assert_log(u'info', u'q1')
        logs.assert_log(u'info', u'q2')


class TestJobCancel(FunctionalRQTestBase):

    def test_existing_job(self):
        '''
        Test cancelling an existing job.
        '''
        job1 = self.enqueue(queue=u'q')
        job2 = self.enqueue(queue=u'q')
        with recorded_logs(u'ckanext.rq.action') as logs:
            call_action(u'job_cancel', id=job1.id)
        all_jobs = self.all_jobs()
        eq(len(all_jobs), 1)
        eq(all_jobs[0], job2)
        assert_raises(KeyError, jobs.job_from_id, job1.id)
        logs.assert_log(u'info', re.escape(job1.id))

    @raises(ObjectNotFound)
    def test_not_existing_job(self):
        call_action(u'job_cancel', id=u'does-not-exist')
