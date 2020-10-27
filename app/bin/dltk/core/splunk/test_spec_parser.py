import unittest

from dltk.test import *
from dltk.core.splunk import spec

__all__ = [
    "SpecParserTestCase"
]


@skip_if_required()
class SpecParserTestCase(unittest.TestCase):

    def runTest(self):

        spec_string = """

        [<name>]
        
        param_a = <string>
        * Line 1.
        * Line 2.
        * Required.

        param_b = <number>
        * Line 1.
        * Line 2.
        * Optional.

        param_c = <bool>

        [<name>:<name>]

        param_d = <password>

        [schema://<name>]

        param_e = <integer>

        """

        test_spec = spec.parse(spec_string)
        self.assertIsNotNone(test_spec)
        self.assertEqual(len(test_spec.stanzas), 3)

        test_stanza = test_spec.get_stanza_for_name("test")
        self.assertIsNotNone(test_stanza)
        self.assertEqual(len(test_stanza.attributes), 3)

        param_a = test_stanza.get_attribute("param_a")
        self.assertIsNotNone(param_a)
        self.assertEqual(param_a.name, "param_a")
        self.assertEqual(param_a.value_spec, "string")
        self.assertEqual(param_a.is_required, True)
        self.assertEqual(len(param_a.docs), 3)

        param_b = test_stanza.get_attribute("param_b")
        self.assertIsNotNone(param_b)
        self.assertEqual(param_b.name, "param_b")
        self.assertEqual(param_b.value_spec, "number")
        self.assertEqual(param_b.is_required, False)
        self.assertEqual(len(param_b.docs), 3)

        param_c = test_stanza.get_attribute("param_c")
        self.assertIsNotNone(param_c)
        self.assertEqual(param_c.name, "param_c")
        self.assertEqual(param_c.value_spec, "bool")
        self.assertEqual(param_c.is_required, False)
        self.assertEqual(len(param_c.docs), 0)

        test_stanza = test_spec.get_stanza_for_name("test:test")
        self.assertIsNotNone(test_stanza)
        self.assertEqual(len(test_stanza.attributes), 1)

        param_d = test_stanza.get_attribute("param_d")
        self.assertIsNotNone(param_d)
        self.assertEqual(param_d.name, "param_d")
        self.assertEqual(param_d.value_spec, "password")
        self.assertEqual(param_d.is_required, False)
        self.assertEqual(len(param_d.docs), 0)

        test_stanza = test_spec.get_stanza_for_name("schema://test")
        self.assertIsNotNone(test_stanza)
        self.assertEqual(len(test_stanza.attributes), 1)

        param_e = test_stanza.get_attribute("param_e")
        self.assertIsNotNone(param_e)
        self.assertEqual(param_e.name, "param_e")
        self.assertEqual(param_e.value_spec, "integer")
        self.assertEqual(param_e.is_required, False)
        self.assertEqual(len(param_e.docs), 0)
