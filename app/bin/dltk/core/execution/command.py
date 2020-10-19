import os
import sys
import logging
import logging.handlers
from dltk.core import model
import time
import csv
import io
import re
import base64
import json
import traceback
from dltk.core.splunk.conf_files_splunk_client import Service as ConfBasedService
import opentracing
import jaeger_client
import socket
from collections import OrderedDict

from dltk.core import deployment
from . context import ExecutionContext
from . result import ExecutionResult
from dltk.core import is_truthy
from . import splunk_protocol
from . import options_parser


# https://conf.splunk.com/files/2017/slides/extending-spl-with-custom-search-commands-and-the-splunk-sdk-for-python.pdf


class ExecutionCommand(object):

    model = None
    deployment = None
    command = None
    buffer = None
    buffer_size = 0
    max_buffer_size = 100000000
    handle_run_number = 0
    fields = None
    dispatch_dir = None
    tracer = None
    trace_scope = None
    trace_id = None
    trace_context_string = None
    context = None
    execution = None

    def __init__(
        self,
        in_file=sys.stdin.buffer,
        out_file=sys.stdout.buffer,
        err_file=sys.stderr,
    ):
        self.in_file = in_file
        self.out_file = out_file
        self.err_file = err_file
        self.getinfo = {}

        splunk_protocol.unmangle_windows_line_endings([
            self.in_file,
            self.out_file,
            self.err_file
        ])

        # Logger instance for user-visible messages.

        self.messages_logger = logging.getLogger("messages")
        self.messages_handler = logging.handlers.BufferingHandler(100000)
        self.messages_logger.addHandler(self.messages_handler)

    def stop_tracing(self):
        if self.tracer:
            if self.trace_scope:
                self.trace_scope.finish()
                self.trace_scope = None
            if hasattr(self.tracer, "close"):
                self.tracer.close()
            self.tracer = None

    def reset_buffer(self):
        # TODO: set initial size depending on max_buffer_size
        #       but make size it is never exceeded.
        self.buffer_size = 0
        self.buffer = io.BytesIO()

    def setup(self):
        logging.info("setting up")
        self.command = self.getinfo['searchinfo']["command"]
        search_id = self.getinfo['searchinfo']["sid"]
        self.dispatch_dir = self.getinfo['searchinfo']["dispatch_dir"]
        logging.info("command name: %s" % self.command)
        is_searchpeer = "searchpeers" in __file__

        command_options = options_parser.parse_options(
            self.getinfo['searchinfo']["args"], [
                "model",
                "method",
                "algorithm",
                "environment",
                "type",
                "max_buffer_size",
                "is_preop",
                "prevent_preop",
                "fields",
                "opentracing_endpoint",
                "opentracing_user",
                "opentracing_password",
                "trace_context",
                "search_id",
                "trace_level",
            ],
            ignore_unknown=True,
        )
        #raise Exception("command_options: %s" % command_options)

        if "search_id" in command_options:
            search_id = command_options["search_id"]

        if "trace_level" in command_options:
            trace_level = command_options["trace_level"]
        else:
            trace_level = ""

        if search_id.startswith("searchparsetmp") or search_id.endswith("_tmp"):
            is_temp_search = True
        else:
            is_temp_search = False
        logging.info("is_temp_search: %s" % is_temp_search)
        if len(search_id) > 20:
            search_id = search_id[-20:]

        app_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        if "fields" not in command_options:
            raise Exception("missing 'fields' parameter")
        self.fields = command_options["fields"].split(",")
        if "is_preop" in command_options:
            is_preop = is_truthy(command_options["is_preop"])
        else:
            is_preop = False
        splunk = ConfBasedService(app_path)

        logging.info("is_preop: %s" % is_preop)
        if "prevent_preop" in command_options:
            prevent_preop = is_truthy(command_options["prevent_preop"])
        else:
            prevent_preop = False
        logging.info("prevent_preop: %s" % prevent_preop)

        if "model" in command_options:
            self.model = model.get(splunk, command_options["model"])
            self.deployment = self.model.deployment
        else:
            if not "algorithm" in command_options:
                raise Exception("missing 'algorithm' parameter")
            algorithm_name = command_options["algorithm"]
            if not "environment" in command_options:
                raise Exception("missing 'environment' parameter")
            environment_name = command_options["environment"]
            self.deployment = deployment.get(splunk, algorithm_name, environment_name)
            if not self.deployment:
                raise Exception("Algorithm \"%s\" is not deployed to environment \"%s\"" % (
                    algorithm_name,
                    environment_name
                ))
            self.model = None

        if not "method" in command_options:
            default_method_name = self.deployment.algorithm.default_method
            if default_method_name:
                method_name = default_method_name
            else:
                raise Exception("missing 'method' parameter. E.g. method=fit")
        else:
            method_name = command_options["method"]
        method = self.deployment.algorithm.get_method(method_name)
        if not method:
            raise Exception("method '%s' does not exist" % method_name)

        if "max_buffer_size" in command_options:
            max_buffer_size = command_options["max_buffer_size"]
        else:
            max_buffer_size = method.max_buffer_size
        if not max_buffer_size or max_buffer_size == "auto":
            # keep initial class value
            pass
        elif self.max_buffer_size == "all":
            self.max_buffer_size = 0
        else:
            self.max_buffer_size = int(self.max_buffer_size)
        self.reset_buffer()

        if not "type" in command_options:
            command_type = method.command_type
        else:
            command_type = command_options["type"]

        opentracing_endpoint = self.deployment.environment.opentracing_endpoint
        opentracing_user = self.deployment.environment.opentracing_user
        opentracing_password = self.deployment.environment.opentracing_password
        if "opentracing_endpoint" in command_options:
            opentracing_endpoint = command_options["opentracing_endpoint"]
        if "opentracing_user" in command_options:
            opentracing_user = command_options["opentracing_user"]
        if "opentracing_password" in command_options:
            opentracing_password = command_options["opentracing_password"]
        if "trace_context" in command_options:
            self.trace_context_string = command_options["trace_context"]

        if opentracing_endpoint and opentracing_user and opentracing_password:
            trace_config = jaeger_client.Config(
                config={
                    'sampler': {
                        'type': 'const',
                        'param': 1,
                    },
                    'logging': False,
                    'jaeger_endpoint': opentracing_endpoint,
                    'jaeger_user': opentracing_user,
                    'jaeger_password': opentracing_password,
                    "propagation": "b3",
                },
                service_name="indexer" if is_searchpeer else "search_head",
                validate=True,
            )
            self.tracer = trace_config.initialize_tracer()
        else:
            self.tracer = opentracing.tracer

        if self.trace_context_string:
            trace_context_bytes = self.trace_context_string.encode()
            trace_context_bytes = base64.b64decode(trace_context_bytes)
            trace_context_dict = json.loads(trace_context_bytes)
            trace_context = opentracing.tracer.extract(
                format=opentracing.propagation.Format.TEXT_MAP,
                carrier=trace_context_dict
            )
        else:
            trace_context = None
        self.trace_scope = self.tracer.start_span(
            "compute-command",
            child_of=trace_context,
            # ignore_active_span
            tags={
                'dltk-method': method_name,
                'dltk-search_id': search_id,
                'dltk-algorithm': self.deployment.algorithm.name,
                'dltk-runtime': self.deployment.algorithm.runtime.name,
                'dltk-environment': self.deployment.environment.name,
                'dltk-preop': is_preop,
                'dltk-command_type': command_type,
            }
        )
        if not self.trace_context_string:
            trace_context_dict = {}
            opentracing.tracer.inject(
                span_context=self.trace_scope,
                format=opentracing.propagation.Format.TEXT_MAP,
                carrier=trace_context_dict
            )
            trace_context_json = json.dumps(trace_context_dict)
            self.trace_context_string = base64.b64encode(trace_context_json.encode()).decode()
        if not trace_context:
            trace_context_dict = {}
            opentracing.tracer.inject(
                span_context=self.trace_scope,
                format=opentracing.propagation.Format.HTTP_HEADERS,
                carrier=trace_context_dict
            )
            if "X-B3-TraceId" in trace_context_dict:
                self.trace_id = trace_context_dict["X-B3-TraceId"]

        if self.deployment.is_disabled:
            raise Exception(
                "Algorithm '%s' disabled for environment '%s'" % (
                    self.deployment.algorithm_name,
                    self.deployment.environment_name,
                ))
        if not self.deployment.is_deployed:
            raise Exception(
                "Algorithm '%s' not yet successfully deployed to environment '%s'. (status: %s message: %s)" % (
                    self.deployment.algorithm_name,
                    self.deployment.environment_name,
                    self.deployment.status,
                    self.deployment.status_message,
                ))
        self.context = ExecutionContext(
            is_preop=is_preop,
            is_searchpeer=is_searchpeer,
            search_id=search_id,
            model=self.model,
            root_trace_context_string=self.trace_context_string,
            method=method,
            message_logger=self.messages_logger,
            fields=self.fields,
            params=command_options
        )

        if not is_temp_search:
            with self.tracer.start_active_span(
                'initialize',
                child_of=self.trace_scope,
            ):
                self.execution = self.deployment.create_execution(self.context)
                try:
                    self.execution.logger.warning("starting execution setup (search=\"%s\")" % self.getinfo['searchinfo']["search"])
                    self.execution.setup()
                    self.execution.logger.warning("execution setup stopped")
                except Exception as e:
                    self.execution.logger.warning(traceback.format_exc())
                    self.die("Unexpected error starting deployment execution: %s" % (
                        ', '.join(traceback.format_exception_only(type(e), e))
                    ))

        # mltk fit: EVENTS
        # mltk apply: streaming or stateful
        info = {
            "type": command_type,
            "required_fields": self.fields,
            # generating
            # maxinputs
        }
        # streaming_preop
        support_preop = method.support_preop and not prevent_preop
        if not is_preop and command_type == "reporting" and support_preop:
            info.update({
                "streaming_preop": "%s is_preop=1 type=streaming %s %s %s %s %s %s %s %s" % (
                    self.command,
                    "search_id=\"%s\"" % search_id,
                    "method=\"%s\"" % method_name,
                    ("model=\"%s\"" % command_options["model"]) if "model" in command_options else "",
                    ("algorithm=\"%s\"" % command_options["algorithm"]) if "algorithm" in command_options else "",
                    ("environment=\"%s\"" % command_options["environment"]) if "environment" in command_options else "",
                    ("max_buffer_size=%s" % command_options["max_buffer_size"]) if "max_buffer_size" in command_options else "",
                    ("fields=\"%s\"" % command_options["fields"]) if "fields" in command_options else "",
                    "trace_context=\"%s\"" % self.trace_context_string,
                ),
            })

        return info

    def handle_chunk(self, metadata, header, chunk):
        final_chunk_from_splunk = metadata.get('finished', False)

        chunk_size = len(chunk)
        self.buffer_size += chunk_size
        self.buffer.write(chunk)
        self.handle_run_number += 1
        self.execution.logger.warning("begin command handler (chunk_size=%s)" % (chunk_size))

        with self.tracer.start_active_span(
            'handle_chunk',
            child_of=self.trace_scope,
            tags={
                "chunk_size": chunk_size,
                "final_chunk_from_splunk": final_chunk_from_splunk,
                "accumulated_buffer_size": self.buffer_size,
                "handle_run_number": self.handle_run_number,
            },
        ) as chunk_scope:

            if final_chunk_from_splunk:
                self.execution.logger.warning("is final chunk from Splunk")
                call_deployment = True
            else:
                if self.max_buffer_size == 0:
                    call_deployment = False
                    self.execution.logger.warning("append to buffer until all data received")
                elif self.buffer_size > self.max_buffer_size:
                    self.execution.logger.warning("max buffer size exceeded")
                    call_deployment = True
                else:
                    call_deployment = False

            if call_deployment:
                with self.tracer.start_active_span(
                    'call_handler',
                    tags={
                        "buffer_size": self.buffer_size,
                    },
                ):
                    try:
                        if self.buffer_size == 0:
                            self.execution.logger.warning("call execution handler (not data)")
                            result = self.execution.handle(None, final_chunk_from_splunk)
                        else:
                            self.execution.logger.warning("call execution handler (%s bytes of data)" % self.buffer_size)
                            self.buffer.seek(0)
                            result = self.execution.handle(self.buffer, final_chunk_from_splunk)
                        if result is None:
                            result = ExecutionResult()
                    except Exception as e:
                        self.execution.logger.warning(traceback.format_exc())
                        result = ExecutionResult(
                            error="Error handling chunk: %s" % (
                                ', '.join(traceback.format_exception_only(type(e), e))
                            ),
                        )
                    finally:
                        self.reset_buffer()
                with self.tracer.start_active_span(
                    'process_results',
                    tags={
                        "event_count": len(result.events),
                    },
                ):
                    if result.error:
                        self.die(result.error)
                    if isinstance(result.events, list):
                        self.execution.logger.warning("got %s results" % len(result.events))
                        field_names = set()
                        for r in result.events:
                            field_names.update(list(r.keys()))
                        out = io.StringIO()
                        writer = csv.DictWriter(out, fieldnames=list(field_names))
                        writer.writeheader()
                        for r in result.events:
                            writer.writerow(r)
                        output_body = out.getvalue()
                    elif isinstance(result.events, str):
                        csv_string = result.events
                        self.execution.logger.warning("got csv result of %s bytes" % len(csv_string))
                        output_body = csv_string
                    else:
                        output_body = None
                finished = final_chunk_from_splunk and result.final
                chunk_scope.span.set_tag("final_response", result.final)
                wait = result.wait
            else:
                finished = False
                output_body = None
                wait = None

        search_status = None
        status_file_path = os.path.join(self.dispatch_dir, "status.csv")
        if os.path.exists(status_file_path):
            with open(status_file_path, mode='r') as f:
                status_reader = csv.DictReader(f)
                for event in status_reader:
                    if "state" in event:
                        search_status = event["state"]
                        break
        if not search_status and not self.execution.context.is_searchpeer:
            self.execution.logger.info("no search status found")
            finished = True
        elif search_status == "FINALIZING":
            self.execution.logger.info("search status=FINALIZING")
            finished = True

        if finished:
            try:
                self.execution.finalize()
            except Exception as e:
                self.execution.logger.warning(traceback.format_exc())
                result = ExecutionResult(
                    error="Unexpected error stopping deployment handler: %s" % (
                        ', '.join(traceback.format_exception_only(type(e), e))
                    ),
                )
            finally:
                self.events = []
            if self.trace_id:
                self.messages_logger.warning("https://app.signalfx.com/#/apm/traces/%s" % self.trace_id)
            self.stop_tracing()

        if output_body:
            result_chunk_size = len(output_body)
        else:
            result_chunk_size = 0
        self.execution.logger.warning("command handler ended (result chunk_size=%s)" % result_chunk_size)

        return {
            'finished': finished
        }, output_body, wait

    def run(self):
        """Handle chunks in a loop until EOF is read.

        If an exception is raised during chunk handling, a chunk
        indicating the error will be written and the process will exit.
        """
        try:
            while self._handle_chunk():
                pass
            self.stop_tracing()
        except Exception as e:
            if isinstance(e, RuntimeError):
                error_message = str(e)
            else:
                error_message = '(%s) %s' % (type(e).__name__, e)
            self.die(error_message)

    def die(self, message, log_traceback=True):
        """Logs a message, writes a user-visible error, and exits."""

        self.messages_logger.error(message)
        if log_traceback:
            self.messages_logger.error(traceback.format_exc())

        self.stop_tracing()

        metadata = {'finished': True, 'error': message}

        # Insert inspector messages from messages_logger.
        messages = self._pop_messages()
        # Convert non-DEBUG messages to ERROR so the user can see them...
        messages = [['ERROR', y] for x, y in messages if x != 'DEBUG']

        if len(messages) > 0:
            metadata.setdefault('inspector', {}).setdefault('messages', []).extend(messages)

        # Sort the keys in reverse order! 'inspector' must come before 'error'.
        metadata = OrderedDict([(k, metadata[k]) for k in sorted(metadata, reverse=True)])

        splunk_protocol.write_chunk(self.out_file, metadata, '')
        sys.exit(1)

    def start_root_scope(self, name, tags=None):
        class DoNothingScope():
            def __enter__(self):
                self.span = self
                return self

            def __exit__(self, type, value, traceback):
                pass

            def set_tag(self, name, value):
                pass

        if self.tracer:
            scope = self.tracer.start_active_span(
                name,
                child_of=self.trace_scope,
                tags=tags,
            )
        else:
            scope = DoNothingScope()
        return scope

    def _handle_chunk(self):
        """Handle (read, process, write) a chunk."""

        with self.start_root_scope(
            "read_data_from_splunk",
            tags={
                opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
            },
        ) as scope:
            ret = splunk_protocol.read_chunk(self.in_file)
            if not ret:
                return False  # EOF

            metadata, header, body = ret

            scope.span.set_tag("bytes", len(body))

        action = metadata.get('action', None)
        logging.info("action: %s" % action)

        # Cache a copy of the getinfo metadata.
        if action == 'getinfo':
            self.getinfo = dict(metadata)
            ret = self.setup()
        else:
            ret = self.handle_chunk(metadata, header, body)

        if isinstance(ret, dict):
            metadata, body, wait = ret, None, None
        else:
            try:
                metadata, body, wait = ret
            except:
                raise TypeError(
                    "Handler must return (metadata, body, sleep), got: %.128s" % repr(ret)
                )

        # Insert inspector messages from messages_logger.
        messages = self._pop_messages()
        if len(messages) > 0:
            metadata.setdefault('inspector', {}).setdefault('messages', []).extend(messages)

        if body is None or len(body) == 0:
            body = ''

        # with self.start_root_scope("write_data_to_splunk", tags={
        #        'bytes': len(body),
        #        opentracing.ext.tags.SPAN_KIND: opentracing.ext.tags.SPAN_KIND_RPC_CLIENT,
        # }):
        splunk_protocol.write_chunk(self.out_file, metadata, body)

        if wait:
            time.sleep(wait)

        return True

    def _pop_messages(self):
        """Drain logging.MemoryHandler holding user-visible messages."""
        messages = []
        for r in self.messages_handler.buffer:
            # Map message levels to Splunk equivalents.
            level = {
                'DEBUG': 'DEBUG',
                'INFO': 'INFO',
                'WARNING': 'WARN',
                'ERROR': 'ERROR',
                'CRITICAL': 'ERROR',
            }[r.levelname]
            messages.append([level, r.getMessage()])

        self.messages_handler.flush()
        return messages
