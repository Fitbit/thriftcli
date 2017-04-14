# Copyright Notice:
# Copyright 2017, Fitbit, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from .thrift_parser import ThriftParser


def convert(request_body):
    """ Converts the Java Thrift request body into an argument dictionary.

    :param request_body: the request body
    :type request_body: str
    :returns: the argument dictionary represented by the request body
    :rtype: dict

    """
    request_body = _clean(request_body)
    field_strings = ThriftParser.split_fields_string(request_body, '([', '])', ',')
    return _convert_from_field_strings(field_strings)


def _clean(request_body):
    """ Removes unused text from the request body for proper parsing.

    For example: AnimalsCollectRequest(ids:[1,2,3]) --> ids:[1,2,3]

    :param request_body: the request body
    :type request_body: str
    :returns: a cleaned request_body that is simpler to parse
    :rtype: str

    """
    try:
        colon_index = request_body.index(':')
        open_paren_index = request_body.index('(')
        if open_paren_index < colon_index:
            close_paren_index = request_body.rindex(')')
            request_body = request_body[open_paren_index+1:close_paren_index]
    except ValueError:
        pass
    return request_body


def _convert_from_field_strings(field_strings):
    """ Converts the list of Java Thrift field strings into an argument dictionary.

    For example: ["ids:[1,2,3]", "log:hi"] ---> {"ids": [1,2,3], "log": "hi"}

    :param field_strings: the list of Java Thrift field strings
    :type field_strings: list of str
    :returns: the argument dictionary represented by the field strings
    :rtype: dict

    """
    return dict([_get_key_and_value(field_string) for field_string in field_strings])


def _get_key_and_value(field_string):
    """ Extracts the key and value from a Java Thrift field string.

    For example: "ids:[1,2,3]" --> "ids", [1,2,3]

    :param field_string: the Java Thrift field string
    :type field_string: str
    :returns: a tuple of key and value of the represented field
    :rtype: tuple of (str, str or Number or JSON)

    """
    colon_index = field_string.index(':')
    open_paren_index = field_string.find('(', 0, colon_index)
    key = field_string[open_paren_index+1:colon_index]
    value_string = field_string[colon_index+1:]
    value = _convert_value_string(value_string)
    return key, value


def _convert_value_string(value_string):
    """ Converts the portion of the Java Thrift field string representing the value into its represented value.

    For example: "[1,2,3]" --> [1,2,3]

    :param value_string: the portion of the Java Thrift field string representing the value
    :type value_string: str
    :returns: the value represented by the value string
    :rtype: str or Number or JSON

    """
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
