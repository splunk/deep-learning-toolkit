import os
import sys

bin_path = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if bin_path not in sys.path:
    sys.path.insert(0, bin_path)
lib_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib"))
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

from splunklib.searchcommands import dispatch
from dltk.core.jobs import JobCommand

if __name__ == "__main__":
    dispatch(JobCommand, sys.argv, sys.stdin, sys.stdout, __name__)
