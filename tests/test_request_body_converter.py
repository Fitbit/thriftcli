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
from __future__ import absolute_import
import unittest
from tests import data
from thriftcli import convert


class TestRequestBodyConverter(unittest.TestCase):

    def test_json_request_body(self):
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY, convert(data.TEST_JSON_REQUEST_BODY))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY2, convert(data.TEST_JSON_REQUEST_BODY2))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY3_ALT, convert(data.TEST_JSON_REQUEST_BODY3))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY4, convert(data.TEST_JSON_REQUEST_BODY4))

    def test_java_thrift_request_body(self):
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY, convert(data.TEST_JAVA_THRIFT_REQUEST_BODY))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY2, convert(data.TEST_JAVA_THRIFT_REQUEST_BODY2))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY3, convert(data.TEST_JAVA_THRIFT_REQUEST_BODY3))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY4, convert(data.TEST_JAVA_THRIFT_REQUEST_BODY4))

    def test_invalid_request_body(self):
        with self.assertRaises(ValueError):
            convert(data.TEST_INVALID_REQUEST_BODY)
