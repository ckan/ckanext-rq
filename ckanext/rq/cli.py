import sys
from optparse import OptionConflictError

from ckan.lib.cli import CkanCommand
import ckan.plugins as p


# Copied from ckan/lib/cli.py with minor changes
class JobsCommand(CkanCommand):
    '''Manage background jobs

    Usage:

        paster jobs worker [--burst] [QUEUES]

            Start a worker that fetches jobs from queues and executes
            them. If no queue names are given then the worker listens
            to the default queue, this is equivalent to

                paster jobs worker default

            If queue names are given then the worker listens to those
            queues and only those:

                paster jobs worker my-custom-queue

            Hence, if you want the worker to listen to the default queue
            and some others then you must list the default queue explicitly:

                paster jobs worker default my-custom-queue

            If the `--burst` option is given then the worker will exit
            as soon as all its queues are empty.

        paster jobs list [QUEUES]

                List currently enqueued jobs from the given queues. If no queue
                names are given then the jobs from all queues are listed.

        paster jobs show ID

                Show details about a specific job.

        paster jobs cancel ID

                Cancel a specific job. Jobs can only be canceled while they are
                enqueued. Once a worker has started executing a job it cannot
                be aborted anymore.

        paster jobs clear [QUEUES]

                Cancel all jobs on the given queues. If no queue names are
                given then ALL queues are cleared.

        paster jobs test [QUEUES]

                Enqueue a test job. If no queue names are given then the job is
                added to the default queue. If queue names are given then a
                separate test job is added to each of the queues.
    '''

    summary = __doc__.split(u'\n')[0]
    usage = __doc__
    min_args = 0

    def __init__(self, *args, **kwargs):
        super(JobsCommand, self).__init__(*args, **kwargs)
        try:
            self.parser.add_option(u'--burst', action='store_true',
                                   default=False,
                                   help=u'Start worker in burst mode.')
        except OptionConflictError:
            # Option has already been added in previous call
            pass

    def command(self):
        self._load_config()
        try:
            cmd = self.args.pop(0)
        except IndexError:
            print(self.__doc__)
            sys.exit(0)
        if cmd == u'worker':
            self.worker()
        elif cmd == u'list':
            self.list()
        elif cmd == u'show':
            self.show()
        elif cmd == u'cancel':
            self.cancel()
        elif cmd == u'clear':
            self.clear()
        elif cmd == u'test':
            self.test()
        else:
            error(u'Unknown command "{}"'.format(cmd))

    def worker(self):
        from ckanext.rq.jobs import Worker
        Worker(self.args).work(burst=self.options.burst)

    def list(self):
        data_dict = {
            u'queues': self.args,
        }
        jobs = p.toolkit.get_action(u'job_list')({}, data_dict)
        for job in jobs:
            if job[u'title'] is None:
                job[u'title'] = ''
            else:
                job[u'title'] = u'"{}"'.format(job[u'title'])
            print(u'{created} {id} {queue} {title}'.format(**job))

    def show(self):
        if not self.args:
            error(u'You must specify a job ID')
        id = self.args[0]
        try:
            job = p.toolkit.get_action(u'job_show')({}, {u'id': id})
        except p.toolkit.ObjectNotFound:
            error(u'There is no job with ID "{}"'.format(id))
        print(u'ID:      {}'.format(job[u'id']))
        if job[u'title'] is None:
            title = u'None'
        else:
            title = u'"{}"'.format(job[u'title'])
        print(u'Title:   {}'.format(title))
        print(u'Created: {}'.format(job[u'created']))
        print(u'Queue:   {}'.format(job[u'queue']))

    def cancel(self):
        if not self.args:
            error(u'You must specify a job ID')
        id = self.args[0]
        try:
            p.toolkit.get_action(u'job_cancel')({}, {u'id': id})
        except p.toolkit.ObjectNotFound:
            error(u'There is no job with ID "{}"'.format(id))
        print(u'Cancelled job {}'.format(id))

    def clear(self):
        data_dict = {
            u'queues': self.args,
        }
        queues = p.toolkit.get_action(u'job_clear')({}, data_dict)
        queues = (u'"{}"'.format(q) for q in queues)
        print(u'Cleared queue(s) {}'.format(u', '.join(queues)))

    def test(self):
        from ckanext.rq.jobs import DEFAULT_QUEUE_NAME, enqueue, test_job
        for queue in (self.args or [DEFAULT_QUEUE_NAME]):
            job = enqueue(test_job, [u'A test job'], title=u'A test job',
                          queue=queue)
            print(u'Added test job {} to queue "{}"'.format(job.id, queue))


def error(msg):
    '''
    Print an error message to STDOUT and exit with return code 1.
    '''
    sys.stderr.write(msg)
    if not msg.endswith('\n'):
        sys.stderr.write('\n')
    sys.exit(1)
