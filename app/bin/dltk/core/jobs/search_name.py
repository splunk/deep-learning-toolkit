import re

search_name_re = re.compile(r"^job:([^:]+):(.+)$")


def format(category, job_name):
    return "job:%s:%s" % (category, job_name)


def parse(search_name):
    match = search_name_re.match(search_name)
    if not match:
        return None, None
    category = match.group(1)
    job_name = match.group(2)
    return category, job_name
