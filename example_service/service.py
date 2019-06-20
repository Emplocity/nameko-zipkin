from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http

from nameko_zipkin import Zipkin


class ExampleService:
    name = 'example_service'
    zipkin = Zipkin()
    example_service = RpcProxy('example_service')

    @rpc
    def traced_method(self):
        return 'Find me in Zipkin!'

    @http('GET', '/')
    def traced_handler(self, request):
        self.zipkin.update_binary_annotations({
            'browser': request.headers.get('User-Agent'),
            'url': request.url,
        })
        return self.example_service.traced_method()
