import os
import sys

bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if bin_path not in sys.path:
    sys.path.insert(0, bin_path)

# Register REST handlers.
# Splunk requires them to be available in a top-level python module.
# See https://docs.splunk.com/Documentation/Splunk/latest/admin/restmapconf: (handler=<SCRIPT>.<CLASSNAME>)

from . core.connector.connector_handlers import *
from . core.algorithm.algorithm_handlers import *
from . core.algorithm.method_handlers import *
from . core.model.rest import *
from . core.environment.environment_handlers import *
from . core.runtime.runtime_handlers import *
from . core.deployment.rest_handlers import *
