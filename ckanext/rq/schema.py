import ckan.plugins as p

get_validator = p.toolkit.get_validator
ignore_missing = get_validator('ignore_missing')
list_of_strings = get_validator('list_of_strings')


def job_list_schema():
    return {
        u'queues': [ignore_missing, list_of_strings],
    }


def job_clear_schema():
    return {
        u'queues': [ignore_missing, list_of_strings],
    }
