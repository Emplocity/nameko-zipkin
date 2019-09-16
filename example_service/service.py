import logging
import logging.config


from nameko.events import EventDispatcher, event_handler
from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http

from nameko_zipkin import Zipkin


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
        "nameko": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
        "": {"handlers": ["console"], "level": "INFO"},
    },
}


logging.getLogger().handlers = []
logging.config.dictConfig(LOGGING)


logger = logging.getLogger(__name__)


class ExampleService:
    name = "example_service"
    zipkin = Zipkin()
    example_service = RpcProxy("example_service")
    dispatch = EventDispatcher()

    @rpc
    def traced_method(self):
        return "Find me in Zipkin!"

    @http("GET", "/")
    def traced_handler(self, request):
        self.zipkin.update_binary_annotations(
            {"browser": request.headers.get("User-Agent"), "url": request.url}
        )
        self.dispatch("request_received", {"url": request.url})
        return self.example_service.traced_method()

    @event_handler("example_service", "request_received")
    def request_received_handler(self, payload):
        logger.info(f"Received request_received event, payload: {payload}")
