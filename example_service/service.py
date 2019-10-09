import logging
import logging.config


from nameko.events import EventDispatcher, event_handler
from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http
from py_zipkin import zipkin

from nameko_zipkin import Zipkin
from nameko_zipkin.utils import stop_span, start_span


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "loggers": {
        "nameko": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "nameko-zipkin": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "": {"handlers": ["console"], "level": "INFO"},
    },
}


logging.getLogger().handlers = []
logging.config.dictConfig(LOGGING)


logger = logging.getLogger(__name__)


class ZipkinEventDispatcher(EventDispatcher):
    def get_message_headers(self, worker_ctx):
        from nameko_zipkin.constants import TRACE_ID_HEADER, PARENT_SPAN_ID_HEADER
        from nameko_zipkin.provider import Zipkin
        container = worker_ctx.container
        zipkin_dependency = [dep for dep in container.dependencies if isinstance(dep, Zipkin)][0]
        logger.info('Found zipkin dependency: {}'.format(zipkin_dependency))
        parent_span = zipkin_dependency.spans.get(worker_ctx.origin_call_id)
        logger.info('Parent span: {}'.format(parent_span))
        headers = super().get_message_headers(worker_ctx)
        if parent_span:
            print(parent_span.zipkin_attrs)
            print(parent_span.zipkin_attrs_override)
            headers[TRACE_ID_HEADER] = parent_span.zipkin_attrs_override.trace_id
            headers[PARENT_SPAN_ID_HEADER] = parent_span.zipkin_attrs_override.span_id
        return headers


class ExampleService:
    name = "example_service"
    zipkin = Zipkin()
    example_service = RpcProxy("example_service")
    dispatch = ZipkinEventDispatcher()

    @rpc
    def traced_method(self):
        return "Find me in Zipkin!"

    @http("GET", "/")
    def traced_handler(self, request):
        self.zipkin.update_binary_annotations(
            {"browser": request.headers.get("User-Agent"), "url": request.url}
        )
        self.dispatch("request_received", {"url": request.url})
        return "asdf" #self.example_service.traced_method()

    @event_handler("example_service", "request_received")
    def request_received_handler(self, payload):
        logger.info(f"Received request_received event, payload: {payload}")
