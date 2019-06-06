import eventlet
import logging

from nameko.extensions import SharedExtension
from py_zipkin.transport import BaseTransportHandler

from nameko_zipkin.constants import (
    ZIPKIN_CONFIG_SECTION, HANDLER_KEY, HANDLER_PARAMS_KEY
)

urllib = eventlet.import_patched('urllib.request')

logger = logging.getLogger('nameko-zipkin')


class HttpHandler(BaseTransportHandler):
    def __init__(self, url):
        self.url = url

    def get_max_payload_bytes(self):
        return None

    def send(self, encoded_span):
        logger.info('posting to {}'.format(self.url))
        request = urllib.Request(
            self.url,
            data=encoded_span,
            headers={'Content-Type': 'application/x-thrift'}
        )
        response = urllib.urlopen(request)
        logger.debug(
            'response [{}]: {}'.format(response.getcode(), response.read().decode())
        )


class Transport(SharedExtension):
    def __init__(self):
        self._handler = None

    def setup(self):
        config = self.container.config[ZIPKIN_CONFIG_SECTION]
        handler_cls = globals()[config[HANDLER_KEY]]
        handler_params = config[HANDLER_PARAMS_KEY]
        self._handler = handler_cls(**handler_params)

    def handle(self, encoded_span):
        self._handler.send(encoded_span)
