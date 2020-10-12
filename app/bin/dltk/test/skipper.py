import unittest
import logging
import os
import re

skip_unless = os.getenv("SKIP_TEST_UNLESS", "")
skip_unless_expression = re.compile("%s" % skip_unless)


def skip_if_required():
    def decorator(cls):
        if skip_unless:
            m = skip_unless_expression.match(cls.__name__)
            if not m:
                #logging.error("skipping %s" % cls.__name__)

                @unittest.skip("skipping %s" % __name__)
                class C(cls):
                    pass
                return C
                #raise C  # unittest.SkipTest()
        return cls
    return decorator
