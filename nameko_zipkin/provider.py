import logging

from nameko.extensions import DependencyProvider
from py_zipkin import zipkin
from py_zipkin.util import generate_random_64bit_string

from nameko_zipkin.constants import *
from nameko_zipkin.transport import Transport
from nameko_zipkin.method_proxy import monkey_patch
from nameko_zipkin.utils import start_span, stop_span


logger = logging.getLogger('nameko-zipkin')


class Zipkin(DependencyProvider):
    transport = Transport()

    def __init__(self):
        self.spans = {}

    def setup(self):
        monkey_patch(self.transport.handle)

    def get_dependency(self, worker_ctx):
        config = self.container.config[ZIPKIN_CONFIG_SECTION]
        zipkin_attrs = _read_zipkin_attrs(worker_ctx)
        logger.debug('get_dependency zipkin attrs: {}'.format(zipkin_attrs))
        span = zipkin.zipkin_server_span(worker_ctx.service_name,
                                         worker_ctx.entrypoint.method_name,
                                         zipkin_attrs=zipkin_attrs,
                                         transport_handler=self.transport.handle,
                                         sample_rate=config.get('SAMPLE_RATE', 10.0))
        logger.debug('tracing {}.{}'.format(worker_ctx.service_name, worker_ctx.entrypoint.method_name))
        self.spans[worker_ctx.call_id] = span
        return span

    def worker_setup(self, worker_ctx):
        span = self.spans.get(worker_ctx.call_id)
        if span:
            logger.debug('starting span for {}.{}'.format(worker_ctx.service_name, worker_ctx.entrypoint.method_name))
            worker_ctx.data[PARENT_SPAN_ID_HEADER] = span.zipkin_attrs_override.span_id
            start_span(span)

    def worker_teardown(self, worker_ctx):
        span = self.spans.get(worker_ctx.call_id)
        if span:
            stop_span(span)
            del self.spans[worker_ctx.call_id]
            logger.debug('stopped span for {}.{}'.format(worker_ctx.service_name, worker_ctx.entrypoint.method_name))


def _read_zipkin_attrs(worker_ctx):
    if TRACE_ID_HEADER not in worker_ctx.data:
        trace_id = generate_random_64bit_string()
        logger.info('No {} header in context, created trace ID: {}'.format(TRACE_ID_HEADER, trace_id))
    else:
        trace_id = worker_ctx.data[TRACE_ID_HEADER]
    return zipkin.ZipkinAttrs(trace_id=trace_id,
                              span_id=generate_random_64bit_string(),
                              parent_span_id=worker_ctx.data.get(PARENT_SPAN_ID_HEADER),
                              flags=worker_ctx.data.get(FLAGS_HEADER),
                              is_sampled=worker_ctx.data.get(SAMPLED_HEADER) == '1')
