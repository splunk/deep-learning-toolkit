import unittest
from dltk.test import *

__all__ = [
    "CreateEnvironmentTest",
    "DeleteEnvironmentTest",
    "ListEnvironmentTestCase",
    "EnvironmentParamsTest",
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


@skip_if_required()
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


class EnvironmentParamsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dltk_environment.create(
            cls.__name__,
            "kubernetes",
            delete_if_already_exists=True,
        )

    def runTest(self):
        ingress_mode_param = dltk_environment.get_environment_param(
            "ingress_mode",
            connector_name="kubernetes"
        )
        self.assertIsNotNone(ingress_mode_param)
        self.assertEqual(ingress_mode_param["name"], "ingress_mode")
        self.assertEqual(ingress_mode_param["default"], "node-port")
        self.assertEqual(ingress_mode_param["value"], None)

        aws_region_name_param = dltk_environment.get_environment_param(
            "aws_region_name",
            connector_name="kubernetes"
        )
        self.assertIsNotNone(ingress_mode_param)
        self.assertEqual(aws_region_name_param["name"], "aws_region_name")
        self.assertEqual(aws_region_name_param["default"], None)
        self.assertEqual(aws_region_name_param["value"], None)

        ingress_mode_param = dltk_environment.get_environment_param(
            "ingress_mode",
            environment_name=self.__class__.__name__
        )
        self.assertIsNotNone(ingress_mode_param)
        self.assertEqual(ingress_mode_param["name"], "ingress_mode")
        self.assertEqual(ingress_mode_param["default"], "node-port")
        self.assertEqual(ingress_mode_param["value"], None)

        aws_region_name_param = dltk_environment.get_environment_param(
            "aws_region_name",
            environment_name=self.__class__.__name__
        )
        self.assertIsNotNone(ingress_mode_param)
        self.assertEqual(aws_region_name_param["name"], "aws_region_name")
        self.assertEqual(aws_region_name_param["default"], None)
        self.assertEqual(aws_region_name_param["value"], None)

        dltk_environment.set_environment_params(
            params={
                "ingress_mode": "1",
                "aws_region_name": "2",
            },
            environment_name=self.__class__.__name__
        )

        ingress_mode_param = dltk_environment.get_environment_param(
            "ingress_mode",
            environment_name=self.__class__.__name__
        )
        self.assertIsNotNone(ingress_mode_param)
        self.assertEqual(ingress_mode_param["name"], "ingress_mode")
        self.assertEqual(ingress_mode_param["default"], "node-port")
        self.assertEqual(ingress_mode_param["value"], "1")

        aws_region_name_param = dltk_environment.get_environment_param(
            "aws_region_name",
            environment_name=self.__class__.__name__
        )
        self.assertIsNotNone(ingress_mode_param)
        self.assertEqual(aws_region_name_param["name"], "aws_region_name")
        self.assertEqual(aws_region_name_param["default"], None)
        self.assertEqual(aws_region_name_param["value"], "2")

    @classmethod
    def tearDownClass(cls):
        dltk_environment.delete(
            cls.__name__,
            skip_if_not_exists=True,
        )
