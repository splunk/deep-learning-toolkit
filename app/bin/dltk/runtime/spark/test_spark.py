import os
import logging
import splunklib.client as client
import splunklib.results as results
from splunklib.binding import HTTPError
import time
import sys
import inspect
import json

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
    "TestEchoingRDD",
    "TestFailingMethod",
]


@dltk_algorithm.algorithm_params(runtime="spark")
@dltk_algorithm.algorithm_params(command_type="reporting")
class SparkTestCase(NotebookAlgorithmTestCase):
    pass


@skip_if_required()
class TestEchoingRDD(SparkTestCase):

    @notebook_method
    def echo_rdd(self, events):
        return events

    def runTest(self):
        query = "| makeresults count=100 | compute algorithm=\"%s\" environment=\"%s\" method=\"%s\" fields=\"_time\"" % (
            self.get_algorithm_name(),
            dltk_environment.get_name(),
            "echo_rdd",
        )
        output_count = len(list(splunk_api.search(query, log_search_log=True, raise_on_error=True)))
        self.assertEqual(output_count, 100, "Unexpected result count")


@skip_if_required()
class TestFailingMethod(SparkTestCase):

    @notebook_method
    def expected_error(self, events):
        raise Exception("expected_error")

    def runTest(self):
        query = "| makeresults count=1 | compute algorithm=\"%s\" environment=\"%s\" method=\"%s\" fields=\"_time\"" % (
            self.get_algorithm_name(),
            dltk_environment.get_name(),
            "expected_error",
        )
        with self.assertRaisesRegex(Exception, 'expected_error'):
            list(splunk_api.search(query, log_search_log=True, raise_on_error=True))


logging.basicConfig(stream=sys.stdout)
root = logging.getLogger()
root.setLevel(logging.INFO)
