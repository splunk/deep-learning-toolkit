from . search_name import parse, format as format_search_name


def get_jobs(splunk, category):
    job_names = []
    for search in splunk.saved_searches:
        parsed_category, job_name = parse(search.name)
        if job_name:
            if parsed_category == category:
                job_names.append(job_name)
    return job_names


def exists(splunk, category, job_name):
    search_name = format_search_name(category, job_name)
    try:
        _ = splunk.saved_searches[search_name]
        return True
    except KeyError:
        return False


__all__ = ["get_jobs", "exists"]
