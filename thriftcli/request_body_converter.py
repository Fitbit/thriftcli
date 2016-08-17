import json_request_body_converter
import java_thrift_request_body_converter

# These converters will be attempted in order. The first to successfully convert the request body will be used.
# Each converter must implement the convert method.
CONVERTERS = [
    json_request_body_converter,
    java_thrift_request_body_converter
]


def convert(request_body):
    """ Converts the request body into an argument dictionary.

    :param request_body: the request body
    :type request_body: str
    :returns: the argument dictionary represented by the request body
    :rtype: dict

    """
    for converter in CONVERTERS:
        try:
            return converter.convert(request_body)
        except ValueError:
            pass
    raise ValueError("Request body is in an unknown format.")
