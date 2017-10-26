import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.rq.action import (
    job_list, job_show, job_clear, job_cancel
)
from ckanext.rq.auth import (
    job_list as job_list_auth,
    job_show as job_show_auth,
    job_clear as job_clear_auth,
    job_cancel as job_cancel_auth
)


class RqPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'rq')

    # IActions

    def get_actions(self):
        return {
            'job_list': job_list,
            'job_show': job_show,
            'job_clear': job_clear,
            'job_cancel': job_cancel,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'job_list': job_list_auth,
            'job_show': job_show_auth,
            'job_clear': job_clear_auth,
            'job_cancel': job_cancel_auth,
        }
