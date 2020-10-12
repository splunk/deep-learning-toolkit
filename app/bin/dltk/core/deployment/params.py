

__all__ = [
    "get_default_param",
]


def get_default_param(name, environment, algorithm=None, runtime=None):
    environment_param = environment.get_param(name)
    if environment_param is not None:
        return environment_param
    if algorithm:
        return algorithm.get_param(name)
    if runtime:
        return runtime.get_param(name)
    return None