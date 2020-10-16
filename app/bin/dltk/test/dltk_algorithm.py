from . import splunk_api
import unittest
from . import dltk_deployment
from functools import wraps
from . import dltk_api


def exists(name):
    algorithms = list_algorithms()
    filtered = list(filter(lambda c: c["name"] == name, algorithms))
    return len(filtered)


def list_algorithms():
    return dltk_api.call(
        "GET",
        "algorithms",
    )


def get_algorithm_params(name):
    return dltk_api.call(
        "GET",
        "algorithm_params", {
            "algorithm": name,
        }
    )


def get_algorithm_param(algorithm_name, param_name):
    params = get_algorithm_params(algorithm_name)
    for p in params:
        if p["name"] == param_name:
            return p
    return None


def set_algorithm_params(algorithm_name, params):
    dltk_api.call(
        "PUT",
        "algorithm_params",
        {
            **{
                "algorithm": algorithm_name,
            },
            **params,
        },
        return_entries=False,
    )


def get_algorithm(name):
    algorithms = list_algorithms()
    filtered = list(filter(lambda c: c["name"] == name, algorithms))
    if not len(filtered):
        raise Exception("cannot find algorithm %s" % name)
    return filtered[0]


def create(name, runtime, params={}, delete_if_already_exists=False):
    if delete_if_already_exists:
        if exists(name):
            delete(name)
    dltk_api.call(
        "POST",
        "algorithms",
        data={
            ** {
                "name": name,
                "runtime": runtime,
            },
            **params
        },
        return_entries=False
    )


def delete(name, skip_if_not_exists=False):
    if skip_if_not_exists:
        if not exists(name):
            return
    dltk_api.call("DELETE", "algorithms", {
        "name": name,
    }, return_entries=False)

    splunk = splunk_api.connect()
    algorithms_conf = splunk.confs["dltk_algorithms"]
    if name in algorithms_conf:
        algorithms_conf.delete(name)
    for stanza in algorithms_conf:
        stanza_name = stanza.name
        i = stanza_name.find(":")
        if i >= 0:
            if stanza_name[:i] == name:
                algorithms_conf.delete(stanza_name)


def list_methods(algorithm_name):
    return dltk_api.call(
        "GET",
        "algorithm_methods",
        data={
            "algorithm": algorithm_name
        }
    )


def get_algorithm_details(algorithm_name):
    return dltk_api.call(
        "GET",
        "algorithm_details",
        data={
            "algorithm": algorithm_name
        }
    )[0]


def set_algorithm_details(algorithm_name, **details):
    return dltk_api.call(
        "PUT",
        "algorithm_details",
        data={
            **{
                "algorithm": algorithm_name
            },
            **details
        }
    )


def check_method_exists(algorithm_name, method_name):
    algorithms = list_methods(algorithm_name)
    filtered = list(filter(lambda c: c["name"] == method_name, algorithms))
    return len(filtered)


def create_method(algorithm_name, method_name, params={}, delete_if_already_exists=False):
    if delete_if_already_exists:
        if check_method_exists(algorithm_name, method_name):
            delete_method(algorithm_name, method_name)
    dltk_api.call(
        "POST",
        "algorithm_methods",
        data={
            **{
                "algorithm": algorithm_name,
                "name": method_name,
            },
            **params
        },
        return_entries=False
    )


def delete_method(algorithm_name, method_name, skip_if_not_exists=False):
    if skip_if_not_exists:
        if not check_method_exists(algorithm_name, method_name):
            return
    dltk_api.call("DELETE", "algorithm_methods", {
        "algorithm": algorithm_name,
        "name": method_name,
    }, return_entries=False)


def algorithm_params(**params):
    def decorator(cls):
        super_func = cls.get_algorithm_params

        @wraps(cls.get_algorithm_params)
        def decorated_func():
            result = super_func()
            result.update(params)
            return result
        cls.get_algorithm_params = decorated_func
        return cls
    return decorator


class AlgorithmTestCase(unittest.TestCase):

    @classmethod
    def get_source_code(cls):
        pass

    @classmethod
    def get_algorithm_name(cls):
        return cls.__name__.lower()

    @classmethod
    def get_algorithm_params(cls):
        return {}

    @classmethod
    def get_algorithm_methods(cls):
        return {}

    @classmethod
    def setUpClass(cls):
        algorithm_name = cls.get_algorithm_name()
        if exists(algorithm_name):
            dltk_deployment.undeploy(algorithm_name)
            delete(algorithm_name)
        try:
            params = cls.get_algorithm_params()
            if "runtime" in params:
                runtime_name = params["runtime"]
                del params["runtime"]
            else:
                runtime_name = None
            create(
                algorithm_name,
                runtime_name,
                params={
                    **{
                        "source_code": cls.get_source_code(),
                        "source_code_version": "1",
                        "deployment_code_version": "1",
                    },
                    **params
                },
                delete_if_already_exists=True,
            )
            for method_name, method_params in cls.get_algorithm_methods().items():
                create_method(algorithm_name, method_name, method_params)
            dltk_deployment.deploy(algorithm_name)
        except:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        algorithm_name = cls.get_algorithm_name()
        dltk_deployment.undeploy(algorithm_name)
        delete(algorithm_name, skip_if_not_exists=True)
