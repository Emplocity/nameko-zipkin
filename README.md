emplocity-nameko-zipkin
-------------

Zipkin tracing for nameko framework

Install
-------

```
pip install emplocity-nameko-zipkin
```

Usage
-----

#### Services

```python
from nameko_zipkin import Zipkin
from nameko.rpc import rpc


class Service:
    name = 'service'
    zipkin = Zipkin() # Dependency provider injects py_zipkin.zipkin.zipkin_span object

    @rpc
    def method(self):
        assert self.zipkin.service_name == Service.name
        assert self.zipkin.span_name == Service.method.__name__
```

#### Standalone rpc

```python
from py_zipkin import zipkin
from nameko_zipkin import monkey_patch
from nameko_zipkin.transport import HttpHandler
from nameko.standalone.rpc import ClusterRpcProxy


handler = HttpHandler('http://localhost:9411/api/v1/spans').handle
monkey_patch(handler)

with zipkin.zipkin_server_span('RootService',
                               'RootMethod',
                               sample_rate=100.,
                               transport_handler=handler):
    with ClusterRpcProxy({'AMQP_URI': "pyamqp://guest:guest@localhost"}) as proxy:
        proxy.service.method()
```

How it works
------------

* monkey_patch patches MethodProxy class to initialize a client span, it's called in dependency provider setup method
* On service method call a server span is created
* Trace parameters (trace_id, parent_span_id, etc.) are passed through context data and are accessible in py_zipkin.thread_local.get_zipkin_attrs
* If there are no parameters, request isn't traced
* Child service calls are also supported
* Trace results are reported through handler classes in nameko_zipkin.transport


Configuration
-------------

ZIPKIN section must be added to nameko service config.yaml

```yaml
ZIPKIN:
    HANDLER: HttpHandler
    HANDLER_PARAMS:
      url: http://localhost:9411/api/v1/spans
```

Test it out locally
-------------------

We've provided an example docker-compose based stack that includes a nameko
service and a Zipkin instance. To try it out, run `docker-compose up` in the
example directory of the project. This will bring up three services: RabbitMQ
(required by nameko), Zipkin, and an example Python service with both RPC
and HTTP endpoints.

Navigate to http://localhost:8000 to visit the example service, and if
you then visit Zipkin dashboard (typically at http://localhost:9411),
you should see some traces there!

Planned changes
---------------

* Kafka transport support
* Custom handlers support in config.yaml ('my_module.MyHandler')
