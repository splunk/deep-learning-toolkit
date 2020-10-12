import os
import sys

bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if bin_path not in sys.path:
    sys.path.insert(0, bin_path)

from dltk.core.execution import ExecutionCommand

if __name__ == "__main__":
    ExecutionCommand().run()
 
