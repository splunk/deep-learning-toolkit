# Modified by SignalFx
# Copyright (c) 2016 Uber Technologies, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
import struct
import time
import sys

from six import reraise
from six.moves import range


class ErrorReporter(object):
    """
    Reports errors by emitting metrics, and if logger is provided,
    logging the error message once every log_interval_minutes

    N.B. metrics will be deprecated in the future
    """

    def __init__(self, metrics, logger=None, log_interval_minutes=15):
        self.logger = logger
        self.log_interval_minutes = log_interval_minutes
        self._last_error_reported_at = time.time()

    def error(self, *args):
        if self.logger is None:
            return

        next_logging_deadline = \
            self._last_error_reported_at + (self.log_interval_minutes * 60)
        current_time = time.time()
        if next_logging_deadline >= current_time:
            # If we aren't yet at the next logging deadline
            return

        self.logger.error(*args)
        self._last_error_reported_at = current_time


def get_boolean(string, default):
    string = str(string).lower()
    if string in ['false', '0', 'none']:
        return False
    elif string in ['true', '1']:
        return True
    else:
        return default


def local_ip():
    """Get the local network IP of this machine"""
    try:
        ip = socket.gethostbyname(socket.gethostname())
    except IOError:
        ip = socket.gethostbyname('localhost')
    # if ip.startswith('127.'):
    #    ip = get_local_ip_by_interfaces()
    #    if ip is None:
    #        ip = get_local_ip_by_socket()
    return ip


def raise_with_value(exception, value):
    """
    Raise an instance of an exception type or reraise an instance with a
    modified message and unchanged traceback.
    """
    _type = exception if isinstance(exception, type) else type(exception)
    reraise(_type, _type(value), sys.exc_info()[2])
