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


# These converters will be attempted in order. The first to successfully convert the request body will be used.
# Each converter must implement the convert method.
from thriftcli import java_thrift_request_body_converter
from thriftcli import json_request_body_converter

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
