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

import time
import logging
import threading

from .constants import DEFAULT_FLUSH_INTERVAL
from .metrics import Metrics, LegacyMetricsFactory
from .utils import ErrorReporter
from six.moves import queue


default_logger = logging.getLogger('jaeger_tracing')


class NullReporter(object):
    """Ignores all spans."""
    def report_span(self, span):
        pass

    def set_process(self, service_name, tags, max_length):
        pass

    def close(self):
        return True


class InMemoryReporter(NullReporter):
    """Stores spans in memory and returns them via get_spans()."""
    def __init__(self):
        super(InMemoryReporter, self).__init__()
        self.spans = []
        self.lock = threading.Lock()

    def report_span(self, span):
        with self.lock:
            self.spans.append(span)

    def get_spans(self):
        with self.lock:
            return self.spans[:]


class LoggingReporter(NullReporter):
    """Logs all spans."""
    def __init__(self, logger=None):
        self.logger = logger if logger else default_logger

    def report_span(self, span):
        self.logger.info('Reporting span %s', span)


class Reporter(NullReporter):
    """Receives completed spans from Tracer and submits them out of process."""
    def __init__(self, sender=None, queue_capacity=100,
                 flush_interval=DEFAULT_FLUSH_INTERVAL, error_reporter=None,
                 metrics=None, metrics_factory=None, **kwargs):
        """
        :param sender: an instance of a senders.Sender subclass for sending
            batches of spans to jaeger.
        :param queue_capacity: how many spans we can hold in memory before
            starting to drop spans
        :param flush_interval: how often the auto-flush is called (in seconds)
        :param error_reporter:
        :param metrics: an instance of Metrics class, or None. This parameter
            has been deprecated, please use metrics_factory instead.
        :param metrics_factory: an instance of MetricsFactory class, or None.
        :param kwargs:
            'logger'
        :return:
        """
        from threading import Lock

        # TODO for next major rev: remove channel param in favor of sender
        # self.agent = Agent.Client()
        self._sender = sender
        self.queue_capacity = queue_capacity
        self.metrics_factory = metrics_factory or LegacyMetricsFactory(metrics or Metrics())
        self.metrics = ReporterMetrics(self.metrics_factory)
        self.error_reporter = error_reporter or ErrorReporter(Metrics())
        self.logger = kwargs.get('logger', default_logger)

        if queue_capacity < self._sender.batch_size:
            raise ValueError('Queue capacity cannot be less than sender batch size')

        self.queue = queue.Queue(maxsize=queue_capacity)
        self.stop = object()  # sentinel
        self.stopped = False
        self.stop_lock = Lock()
        self.flush_interval = flush_interval or None
        self._min_flush_interval = 10 ** -9
        self._consume_queue_thread = None

    def set_process(self, service_name, tags, max_length):
        self._sender.set_process(service_name, tags, max_length)

    def report_span(self, span):
        """
        Add a finished span to the queue, creating a `self._consume_queue()` worker thread
        if none exists.  This deferred creation of the consumer thread allows for easy adoption
        in forking environments (e.g. Django) where background threads shouldn't be spawned
        until the application is actively traced.
        """
        if self._consume_queue_thread is None:
            self._consume_queue_thread = threading.Thread(target=self._consume_queue)
            self._consume_queue_thread.daemon = True
            self._consume_queue_thread.start()

        try:
            with self.stop_lock:
                stopped = self.stopped
            if stopped:
                self.metrics.reporter_dropped(1)
            else:
                self.queue.put_nowait(span)
        except queue.Full:
            self.metrics.reporter_dropped(1)

    def _consume_queue(self):
        stopped = False
        while not stopped:
            interval = self.flush_interval
            spans_appended = 0
            while True:
                t0 = time.time()
                timeout = max(interval, self._min_flush_interval) if self.flush_interval else None
                try:
                    span = self.queue.get(timeout=timeout)
                    t1 = time.time()
                except queue.Empty:
                    # Always flush on timeouts, as they signify interval completion
                    break

                if span == self.stop:
                    stopped = True
                    self.queue.task_done()
                    break

                spans_appended += 1
                try:
                    spans_reported = self._sender.append(span)
                except Exception as exc:
                    # Assume append() triggered flush(), which failed and
                    # included all previously appended spans
                    self.metrics.reporter_failure(spans_appended)
                    self.error_reporter.error(exc)
                    for _ in range(spans_appended):
                        self.queue.task_done()
                    spans_appended = 0
                else:
                    if spans_reported:
                        self.metrics.reporter_success(spans_reported)
                        for _ in range(spans_reported):
                            self.queue.task_done()
                        spans_appended -= spans_reported

                if self.flush_interval:
                    interval -= t1 - t0

            try:
                try:
                    spans_reported = self._sender.flush()
                except Exception as exc:
                    # Assume number of failed spans is equal to previously appended
                    self.metrics.reporter_failure(spans_appended)
                    self.error_reporter.error(exc)
                    for _ in range(spans_appended):
                        self.queue.task_done()
                else:
                    self.metrics.reporter_success(spans_reported)
                    for _ in range(spans_reported):
                        self.queue.task_done()
                    self.metrics.reporter_queue_length(self.queue.qsize())
            except Exception as exc:
                self.logger.error(exc)
                break

        self.logger.info('Span publisher exited')

    def close(self):
        """
        Ensure that all spans from the queue are submitted.
        """
        with self.stop_lock:
            self.stopped = True
        if self._consume_queue_thread is not None:
            if self._consume_queue_thread.is_alive():
                self.queue.put(self.stop)
                self.queue.join()
            self._consume_queue_thread.join()

        return True


class ReporterMetrics(object):
    """Reporter specific metrics."""

    def __init__(self, metrics_factory):
        self.reporter_success = \
            metrics_factory.create_counter(name='jaeger:reporter_spans', tags={'result': 'ok'})
        self.reporter_failure = \
            metrics_factory.create_counter(name='jaeger:reporter_spans', tags={'result': 'err'})
        self.reporter_dropped = \
            metrics_factory.create_counter(name='jaeger:reporter_spans', tags={'result': 'dropped'})
        self.reporter_queue_length = \
            metrics_factory.create_gauge(name='jaeger:reporter_queue_length')


class CompositeReporter(NullReporter):
    """Delegates reporting to one or more underlying reporters."""
    def __init__(self, *reporters):
        self.reporters = reporters

    def set_process(self, service_name, tags, max_length):
        for reporter in self.reporters:
            reporter.set_process(service_name, tags, max_length)

    def report_span(self, span):
        for reporter in self.reporters:
            reporter.report_span(span)

    def close(self):
        closed = [reporter.close() for reporter in self.reporters]
        return all(closed)
