import inspect
import sys
import unittest

from dltk.core.splunk.test_spec_parser import *
from dltk.connector.kubernetes.test_resources import *
from dltk.core.runtime.test_runtime_api import *
from dltk.core.environment.test_environment import *
from dltk.core.algorithm.test_algorithm_api import *
from dltk.core.algorithm.test_method_api import *
from dltk.core.deployment.test_deployment_api import *
from dltk.runtime.base.test_base import *
from dltk.runtime.spark.test_spark import *

test_names = []
for name in dir():
    t = getattr(sys.modules[__name__], name)
    if inspect.isclass(t):
        if issubclass(t, unittest.TestCase):
            test_names.append(name)

__all__ = test_names
