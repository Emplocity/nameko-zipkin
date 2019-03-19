import logging

import eventlet
from nameko.extensions import SharedExtension
from py_zipkin.transport import BaseTransportHandler

from nameko_zipkin.constants import *


requests = eventlet.import_patched('requests')

logger = logging.getLogger('nameko-zipkin')


class HttpHandler(BaseTransportHandler):
    def __init__(self, url):
        self.url = url

    def get_max_payload_bytes(self):
        return None

    def send(self, encoded_span):
        logger.info('posting to {}'.format(self.url))
        response = requests.post(
            self.url,
            data=encoded_span,
            headers={'Content-Type': 'application/x-thrift'},
        )
        logger.debug('response [{}]: {}'.format(response.status_code, response.text))


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
