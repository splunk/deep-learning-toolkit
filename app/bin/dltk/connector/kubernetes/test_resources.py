import unittest

from dltk.test import *
from . import resources

__all__ = [
    "MemoryResourcesParserTestCase",
    "CPUResourcesParserTestCase",
]


@skip_if_required()
class CPUResourcesParserTestCase(unittest.TestCase):

    def runTest(self):
        self.assertEqual(resources.parse_cpu("2"), 2)
        self.assertEqual(resources.parse_cpu("2000m"), 2)
        self.assertEqual(resources.parse_cpu("1500m"), 1.5)
        
@skip_if_required()
class MemoryResourcesParserTestCase(unittest.TestCase):

    def runTest(self):

        self.assertEqual(resources.parse_memory("10Gi"), 10*1024*1024*1024)
        self.assertEqual(resources.parse_memory("10G"), 10*1000*1000*1000)
        self.assertEqual(resources.parse_memory("100Mi"), 100*1024*1024)
        self.assertEqual(resources.parse_memory("100M"), 100*1000*1000)
        self.assertEqual(resources.parse_memory("2048Mi"), resources.parse_memory("2Gi"))
