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

from __future__ import absolute_import

import threading
import time


class PeriodicCallback(object):
    """
    Thread-based implementation of tornado.io_loop.PeriodicCallback:
    Schedules the given callback to be called periodically in a background thread.

    The callback is called every ``callback_time`` milliseconds.

    If the callback runs for longer than ``callback_time`` milliseconds,
    subsequent invocations will be skipped.

    `start` must be called after the `PeriodicCallback` is created.
    """

    def __init__(self, callback, callback_time):
        self.callback = callback
        if callback_time < 0:
            raise ValueError('callback_time must be positive')
        self.callback_time = callback_time
        self._scheduler_sleep = callback_time / 1000.0
        self._running = False
        self._lock = threading.Lock()
        self._scheduler_thread = None
        self._callback_thread = None

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            if self._scheduler_thread is None:
                self._scheduler_thread = threading.Thread(target=self._scheduler)
                self._scheduler_thread.daemon = True
                self._scheduler_thread.start()

    def stop(self):
        with self._lock:
            if self._running:
                self._running = False

            if self._scheduler_thread is not None:
                self._scheduler_thread.join()
                self._scheduler_thread = None
            if self._callback_thread is not None:
                self._callback_thread.join()
                self._callback_thread = None

    def _scheduler(self):
        while self._running:
            if self._callback_thread:
                if not self._callback_thread.is_alive():
                    self._callback_thread.join()
                    self._callback_thread = None
            if self._callback_thread is None:
                self._callback_thread = threading.Thread(target=self.callback)
                self._callback_thread.daemon = True
                self._callback_thread.start()

            time.sleep(self._scheduler_sleep)
