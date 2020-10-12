class JobException(Exception):
    pass


class Stop(JobException):
    pass


class Repeat(JobException):
    pass
