import unittest
from dltk.test import *

__all__ = [
    "CreateEnvironmentTest",
    "ListEnvironmentTestCase",
    "DeleteEnvironmentTest",
]


@skip_if_required()
class CreateEnvironmentTest(unittest.TestCase):

    def runTest(self):
        dltk_environment.create(
            self.__class__.__name__,
            "kubernetes",
            delete_if_already_exists=True,
        )

    @classmethod
    def tearDownClass(cls):
        dltk_environment.delete(
            cls.__name__,
        )


@skip_if_required()
class ListEnvironmentTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dltk_environment.create(
            cls.__name__,
            "kubernetes",
            delete_if_already_exists=True,
        )

    def runTest(self):
        name = self.__class__.__name__
        environments = dltk_environment.get_all()
        found = False
        for e in environments:
            if e["name"] == name:
                found = True
        self.assertTrue(found, "could not find environment %s in %s" % (
            name,
            environments,
        ))

    @classmethod
    def tearDownClass(cls):
        dltk_environment.delete(
            cls.__name__,
        )

class DeleteEnvironmentTest(unittest.TestCase):

    def runTest(self):
        dltk_environment.create(
            self.__class__.__name__,
            "kubernetes",
            delete_if_already_exists=True,
        )

        environments = dltk_environment.get_all()
        found = False
        for e in environments:
            if e["name"] == self.__class__.__name__:
                found = True
        self.assertTrue(found, "could not find environment %s in %s" % (
            self.__class__.__name__,
            environments,
        ))

        dltk_environment.delete(
            self.__class__.__name__,
        )

        environments = dltk_environment.get_all()
        found = False
        for e in environments:
            if e["name"] == self.__class__.__name__:
                found = True
        self.assertFalse(found, "found environment %s in %s" % (
            self.__class__.__name__,
            environments,
        ))

    @classmethod
    def tearDownClass(cls):
        dltk_environment.delete(
            cls.__name__,
            skip_if_not_exists=True,
        )
