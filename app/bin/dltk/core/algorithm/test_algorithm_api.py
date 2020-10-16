import unittest

from dltk.test import *

__all__ = [
    "ListAlgorithmsTestCase",
    "AlgorithmParamsTestCase",
    "AlgorithmDetailsTestCase",
]


@skip_if_required()
class AlgorithmParamsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runtime_name = "%sRuntime" % cls.__name__
        cls.connector_name = "%sConnector" % cls.__name__
        cls.algorithm_name = "%sAlgorithm" % cls.__name__

    def runTest(self):
        dltk_connector.create(
            name=self.connector_name,
            delete_if_already_exists=True,
        )
        dltk_runtimes.create(
            name=self.runtime_name,
            connector=self.connector_name,
            delete_if_already_exists=True,
            params={
                "algorithm_params": "a,b"
            }
        )
        a_param = dltk_runtimes.get_algorithm_param(self.runtime_name, "a")
        self.assertEqual(a_param["default"], None)
        dltk_runtimes.set_algorithm_params(
            self.runtime_name, {
                "a": "a"
            }
        )
        a_param = dltk_runtimes.get_algorithm_param(self.runtime_name, "a")
        self.assertEqual(a_param["default"], "a")

        dltk_algorithm.create(
            name=self.algorithm_name,
            runtime=self.runtime_name,
            delete_if_already_exists=True,
        )
        a_param = dltk_algorithm.get_algorithm_param(self.algorithm_name, "a")
        self.assertEqual(a_param["default"], "a")
        dltk_algorithm.set_algorithm_params(
            self.algorithm_name, {
                "a": "aa"
            }
        )
        a_param = dltk_algorithm.get_algorithm_param(self.algorithm_name, "a")
        self.assertEqual(a_param["value"], "aa")

    @classmethod
    def tearDownClass(cls):
        dltk_algorithm.delete(
            name=cls.algorithm_name,
            skip_if_not_exists=True,
        )
        dltk_runtimes.delete(
            name=cls.runtime_name,
            skip_if_not_exists=True,
        )
        dltk_connector.delete(
            name=cls.connector_name,
            skip_if_not_exists=True,
        )


@skip_if_required()
class ListAlgorithmsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runtime_name = "%sRuntime" % cls.__name__
        cls.connector_name = "%sConnector" % cls.__name__
        cls.algorithm_name = "%sAlgorithm" % cls.__name__
        cls.method_name = "test"
        try:
            dltk_connector.create(
                name=cls.connector_name,
                delete_if_already_exists=True,
            )
            dltk_runtimes.create(
                name=cls.runtime_name,
                connector=cls.connector_name,
                delete_if_already_exists=True,
            )
            dltk_algorithm.create(
                name=cls.algorithm_name,
                runtime=cls.runtime_name,
                delete_if_already_exists=True,
            )
        except:
            cls.tearDownClass()
            raise

    def runTest(self):
        algorithms = dltk_algorithm.list_algorithms()
        found = False
        for r in algorithms:
            if r["name"] == self.algorithm_name:
                found = True
        self.assertTrue(found, "could not find algorithm '%s'" % self.algorithm_name)

    @ classmethod
    def tearDownClass(cls):
        dltk_algorithm.delete(
            name=cls.algorithm_name,
            skip_if_not_exists=True,
        )
        dltk_runtimes.delete(
            name=cls.runtime_name,
            skip_if_not_exists=True,
        )
        dltk_connector.delete(
            name=cls.connector_name,
            skip_if_not_exists=True,
        )


@skip_if_required()
class AlgorithmDetailsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runtime_name = "%sRuntime" % cls.__name__
        cls.connector_name = "%sConnector" % cls.__name__
        cls.algorithm_name = "%sAlgorithm" % cls.__name__
        try:
            dltk_connector.create(
                name=cls.connector_name,
                delete_if_already_exists=True,
            )
            dltk_runtimes.create(
                name=cls.runtime_name,
                connector=cls.connector_name,
                delete_if_already_exists=True,
            )
            dltk_algorithm.create(
                name=cls.algorithm_name,
                runtime=cls.runtime_name,
                delete_if_already_exists=True,
            )
        except:
            cls.tearDownClass()
            raise

    def runTest(self):
        details = dltk_algorithm.get_algorithm_details(
            algorithm_name=self.__class__.algorithm_name,
        )
        self.assertEqual(details["description"], "")
        dltk_algorithm.set_algorithm_details(
            algorithm_name=self.__class__.algorithm_name,
            description="ddd",
        )
        details = dltk_algorithm.get_algorithm_details(
            algorithm_name=self.__class__.algorithm_name,
        )
        self.assertEqual(details["description"], "ddd")

        details = dltk_algorithm.get_algorithm_details(
            algorithm_name=self.__class__.algorithm_name,
        )
        self.assertEqual(details["category"], "")
        dltk_algorithm.set_algorithm_details(
            algorithm_name=self.__class__.algorithm_name,
            category="ccc",
        )
        details = dltk_algorithm.get_algorithm_details(
            algorithm_name=self.__class__.algorithm_name,
        )
        self.assertEqual(details["category"], "ccc")

    @ classmethod
    def tearDownClass(cls):
        dltk_algorithm.delete(
            name=cls.algorithm_name,
            skip_if_not_exists=True,
        )
        dltk_runtimes.delete(
            name=cls.runtime_name,
            skip_if_not_exists=True,
        )
        dltk_connector.delete(
            name=cls.connector_name,
            skip_if_not_exists=True,
        )
