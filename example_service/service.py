from nameko.rpc import rpc
from nameko.web.handlers import http

from nameko_zipkin import Zipkin


class ExampleService:
    name = 'example_service'
    zipkin = Zipkin()

    @rpc
    def traced_method(self):
        return 'Find me in Zipkin!'

    @http('GET', '/')
    def traced_handler(self, request):
        return 'Find me in Zipkin!'
