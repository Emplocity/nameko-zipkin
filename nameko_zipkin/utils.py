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
    logger.debug(
        '%s span started [%s]: %s -> %s',
        attrs.get('type'),
        attrs.get('trace_id'),
        attrs.get('parent_span_id'),
        attrs.get('span_id'),
        extra=attrs,
    )


def stop_span(span):
    attrs = _get_attrs(span)
    try:
        span.stop()
    except:
        logger.error('Exception on span stop', exc_info=True, extra=attrs)
    finally:
        if span.zipkin_attrs:
            logger.debug(
                '%s span stopped [%s]: %s <- %s',
                attrs.get('type'),
                attrs.get('trace_id'),
                attrs.get('span_id'),
                attrs.get('parent_span_id'),
                extra=attrs,
            )
