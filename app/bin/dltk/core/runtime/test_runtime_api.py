import unittest

from dltk.test import *

__all__ = [
    "ListRuntimesTestCase"
]


@skip_if_required()
class ListRuntimesTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runtime_name = cls.__name__
        try:
            dltk_runtimes.create(
                name=cls.runtime_name,
                connector="dummy",
            )
        except:
            cls.tearDownClass()
            raise

    def runTest(self):
        runtimes = dltk_api.call("GET", "runtimes")
        found = False
        for r in runtimes:
            if r["name"] == self.runtime_name:
                found = True
        self.assertTrue(found, "could not find %s runtime" % self.runtime_name)

    @classmethod
    def tearDownClass(cls):
        dltk_runtimes.delete(
            name=cls.runtime_name,
        )
