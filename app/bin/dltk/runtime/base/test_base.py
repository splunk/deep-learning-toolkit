import logging
import sys

from dltk.test import *
from dltk.test.dltk_algorithm import *
from dltk.test.dltk_algorithm_notebook_testcase import *


def setUpModule():
    dltk_environment.set_up()
    dltk_runtimes.set_up()


def tearDownModule():
    dltk_runtimes.tear_down()
    dltk_environment.tear_down()


__all__ = [
    "TestEchoingDataBaseRuntime",
]


@dltk_algorithm.deployment_params(
    store_models_in_volume=False,
)
@dltk_algorithm.algorithm_params(
    runtime="base",
    command_type="reporting",
)
class BaseRuntimeTestCase(NotebookAlgorithmTestCase):
    @classmethod
    def get_default_cell_metadata(cls):
        return {
            "name": "dltk",
        }


@skip_if_required()
class TestEchoingDataBaseRuntime(BaseRuntimeTestCase):

    @notebook_method
    def init(df, param):  # noqa
        return {}

    @notebook_method
    def summary(model=None):  # noqa
        return {}

    @notebook_method
    def fit(model, df, param):  # noqa
        return df

    @notebook_method
    def apply(model, df, param):  # noqa
        return df

    @notebook_method
    def save(model, name):  # noqa
        return model

    @notebook_method
    def load(name):  # noqa
        return {}

    def runTest(self):
        query = "| makeresults count=100 | compute algorithm=\"%s\" environment=\"%s\" method=\"%s\" fields=\"_time\"" % (
            self.get_algorithm_name(),
            dltk_environment.get_name(),
            "fit",
        )
        output_count = len(list(splunk_api.search(query, log_search_log=True, raise_on_error=True)))
        self.assertEqual(output_count, 100, "Unexpected result count")


logging.basicConfig(stream=sys.stdout)
root = logging.getLogger()
root.setLevel(logging.INFO)
