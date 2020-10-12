import unittest

from dltk.test import *

__all__ = [
    "ListMethodsTestCase"
]

@skip_if_required()
class ListMethodsTestCase(unittest.TestCase):

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
            dltk_algorithm.create_method(
                algorithm_name=cls.algorithm_name,
                method_name=cls.method_name,
                delete_if_already_exists=True,
            )
        except:
            cls.tearDownClass()
            raise

    def runTest(self):
        methods = dltk_algorithm.list_methods(self.algorithm_name)
        found = False
        for m in methods:
            if m["name"] == self.method_name:
                found = True
        self.assertTrue(found, "could not find method for algorithm")

    @ classmethod
    def tearDownClass(cls):
        dltk_algorithm.delete_method(
            algorithm_name=cls.algorithm_name,
            method_name=cls.method_name,
            skip_if_not_exists=True,
        )
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
