import logging

from py_zipkin.zipkin import zipkin_client_span

logger = logging.getLogger('nameko-zipkin')


def _get_attrs(span):
    attrs = span.zipkin_attrs._asdict() if span.zipkin_attrs else {}
    attrs['type'] = 'client' if type(span) is zipkin_client_span else 'server'
    return attrs


def start_span(span):
    span.start()
    attrs = _get_attrs(span)
    logger.debug('{type} span started [{trace_id}]: {parent_span_id} -> {span_id}'.format(**attrs), extra=attrs)


def stop_span(span):
    attrs = _get_attrs(span)
    try:
        span.stop()
    except:
        logger.error('Exception on span stop', exc_info=True, extra=attrs)
    finally:
        if span.zipkin_attrs:
            logger.debug('{type} span stopped [{trace_id}]: {span_id} <- {parent_span_id}'.format(**attrs), extra=attrs)
