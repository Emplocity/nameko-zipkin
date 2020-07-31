from nameko.rpc import rpc, RpcProxy
from nameko.web.handlers import http

from nameko_zipkin import Zipkin


class MyService:
    name = "my_service"
    my_service = RpcProxy(name)
    zipkin = Zipkin()

    @rpc
    def generate_response(self):
        return "Find me in Zipkin!"

    @http("GET", "/")
    def show_homepage(self, request):
        self.zipkin.update_binary_annotations(
            {"browser": request.headers.get("User-Agent"), "url": request.url}
        )
        return self.my_service.generate_response()
