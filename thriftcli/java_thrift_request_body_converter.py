import json
from .thrift_parser import ThriftParser


def convert(request_body):
    """ Converts the Java Thrift request body into an argument dictionary.

    :param request_body: The request body
    :type request_body: str
    :returns: The argument dictionary represented by the request body
    :rtype: dict

    """
    field_strings = ThriftParser.split_fields_string(request_body, '([', '])', ',')
    return _convert_from_field_strings(field_strings)


def _convert_from_field_strings(field_strings):
    args = {}
    for field_string in field_strings:
        colon_index = field_string.index(':')
        key = field_string[:colon_index]
        value_string = field_string[colon_index+1:]
        args[key] = _convert_value_string(value_string)
    return args


def _convert_value_string(value_string):
    try:
        open_paren_index = value_string.index('(')
        close_paren_index = value_string.rindex(')')
        value_string = value_string[open_paren_index+1:close_paren_index]
        return convert(value_string)
    except ValueError:
        try:
            return json.loads(value_string)
        except ValueError:
            return value_string
