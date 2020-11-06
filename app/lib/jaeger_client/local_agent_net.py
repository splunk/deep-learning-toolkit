# Modified by SignalFx
# Copyright (c) 2016-2018 Uber Technologies, Inc.
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

from requests import Session
from .TUDPTransport import TUDPTransport
from thrift.transport.TTransport import TBufferedTransport


class LocalAgentHTTP(object):

    DEFAULT_TIMEOUT = 15

    def __init__(self, host, port):
        self.agent_http_host = host
        self.agent_http_port = int(port)
        self._http_client = Session()

    def _request(self, path, timeout=DEFAULT_TIMEOUT, args=None):
        url = 'http://%s:%d/%s' % (self.agent_http_host, self.agent_http_port, path)
        return self._http_client.get(url, timeout=timeout, params=args)

    def request_sampling_strategy(self, service_name, timeout=DEFAULT_TIMEOUT):
        return self._request('sampling', timeout=timeout, args={'service': service_name})

    def request_throttling_credits(self,
                                   service_name,
                                   client_id,
                                   operations,
                                   timeout=DEFAULT_TIMEOUT):
        return self._request('credits', timeout=timeout, args=[
            ('service', service_name),
            ('uuid', client_id),
        ] + [('operations', op) for op in operations])


class LocalAgentReader(object):
    """
    LocalAgentReader implements what is necessary to obtain sampling strategies
    and throttling credits from the local jaeger-agent.
    """

    def __init__(self, host, sampling_port, reporting_port, throttling_port=None):
        self._reporting_port = reporting_port
        self._host = host

        # HTTP sampling
        self.local_agent_http = LocalAgentHTTP(host, sampling_port)

        # HTTP throttling
        if throttling_port:
            self.throttling_http = LocalAgentHTTP(host, throttling_port)

    # Pass-through for HTTP sampling strategies request.
    def request_sampling_strategy(self, *args, **kwargs):
        return self.local_agent_http.request_sampling_strategy(*args, **kwargs)

    # Pass-through for HTTP throttling credit request.
    def request_throttling_credits(self, *args, **kwargs):
        return self.throttling_http.request_throttling_credits(*args, **kwargs)


class LocalAgentSender(LocalAgentReader, TBufferedTransport):
    """
    LocalAgentSender implements everything necessary to report spans to
    the local jaeger-agent.

    NOTE: LocalAgentSender derives from TBufferedTransport. This will buffer
    up all written data until flush() is called. Flush gets called at the
    end of the batch span submission call.
    """
    def __init__(self, host, sampling_port, reporting_port, throttling_port=None):
        LocalAgentReader.__init__(self, host, sampling_port, reporting_port, throttling_port)
        # UDP reporting - this will only get written to after our flush() call.
        # We are buffering things up because we are a TBufferedTransport.
        udp = TUDPTransport(host, reporting_port)
        TBufferedTransport.__init__(self, udp)
