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
import sys
import unittest

import mock

from tests import data
from tests.data.generated.Sample.ttypes import SampleResponse
from thriftcli import thrift_cli, ThriftCLIError


class TestThriftCLI(unittest.TestCase):
    @mock.patch('thriftcli.thrift_cli._load_file')
    @mock.patch('os.path.isfile')
    def test_parse_args(self, mock_isfile, mock_load_file):
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS):
            args = thrift_cli._parse_namespace(thrift_cli._parse_args())
            expected_args = data.TEST_PARSED_ARGS
            self.assertEqual(args, expected_args)
        with self.assertRaises(ThriftCLIError), mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS2):
            mock_isfile.return_value = False
            thrift_cli._parse_namespace(thrift_cli._parse_args())
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS2):
            mock_isfile.return_value = True
            mock_load_file.return_value = data.TEST_JSON_REQUEST_BODY
            args = thrift_cli._parse_namespace(thrift_cli._parse_args())
            expected_args = data.TEST_PARSED_ARGS2
            self.assertEqual(args, expected_args)
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS3):
            args = thrift_cli._parse_namespace(thrift_cli._parse_args())
            expected_args = data.TEST_PARSED_ARGS3
            self.assertEqual(args, expected_args)
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS4):
            args = thrift_cli._parse_namespace(thrift_cli._parse_args())
            expected_args = data.TEST_PARSED_ARGS4
            self.assertEqual(args, expected_args)
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS6):
            args = thrift_cli._parse_namespace(thrift_cli._parse_args())
            expected_args = data.TEST_PARSED_ARGS6
            self.assertEqual(args, expected_args)
        with self.assertRaises(ThriftCLIError), mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS2):
            mock_isfile.return_value = True
            mock_load_file.return_value = data.TEST_INVALID_REQUEST_BODY
            thrift_cli._parse_namespace(thrift_cli._parse_args())
        with self.assertRaises(ThriftCLIError), mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS5):
            thrift_cli._parse_namespace(thrift_cli._parse_args())

    def test_split_endpoint(self):
        endpoint = '%s.%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        expected_service_name, expected_method_name = data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME
        service_name, method_name = thrift_cli._split_endpoint(endpoint)
        self.assertEqual((service_name, method_name), (expected_service_name, expected_method_name))
        endpoint = '%s%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIError):
            thrift_cli._split_endpoint(endpoint)
        endpoint = '%s.%s.abc' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIError):
            thrift_cli._split_endpoint(endpoint)

    def test_return_json_with_sets(self):
        response = SampleResponse(message='test', tags={'tag1', 'tag2', 'tag3'})
        json_response = thrift_cli.ThriftCLI.transform_output(response, return_json=True)
        resp = json.loads(json_response)
        self.assertEqual(len(resp['tags']), 3)
