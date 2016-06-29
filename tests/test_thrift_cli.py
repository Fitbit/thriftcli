import sys
import unittest

import mock

import data
from thriftcli import thrift_cli, ThriftCLI, ThriftCLIError


class TestThriftCLI(unittest.TestCase):
    @mock.patch('thriftcli.thrift_cli._load_file')
    @mock.patch('os.path.isfile')
    def test_parse_args(self, mock_isfile, mock_load_file):
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS):
            args = thrift_cli._parse_args()
            expected_args = data.TEST_PARSED_ARGS
            self.assertEqual(args, expected_args)
        with self.assertRaises(ThriftCLIError), mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS2):
            mock_isfile.return_value = False
            thrift_cli._parse_args()
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS2):
            mock_isfile.return_value = True
            mock_load_file.return_value = data.TEST_JSON_STRING
            args = thrift_cli._parse_args()
            expected_args = data.TEST_PARSED_ARGS2
            self.assertEqual(args, expected_args)
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS3):
            args = thrift_cli._parse_args()
            expected_args = data.TEST_PARSED_ARGS3
            self.assertEqual(args, expected_args)
        with mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS4):
            args = thrift_cli._parse_args()
            expected_args = data.TEST_PARSED_ARGS4
            self.assertEqual(args, expected_args)
        with self.assertRaises(ThriftCLIError), mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS2):
            mock_isfile.return_value = True
            mock_load_file.return_value = data.TEST_INVALID_JSON_STRING
            thrift_cli._parse_args()
        with self.assertRaises(ThriftCLIError), mock.patch.object(sys, 'argv', data.TEST_CLI_ARGS5):
            thrift_cli._parse_args()

    def test_split_endpoint(self):
        endpoint = '%s.%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        expected_service_name, expected_method_name = data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME
        service_name, method_name = ThriftCLI._split_endpoint(endpoint)
        self.assertEqual((service_name, method_name), (expected_service_name, expected_method_name))
        endpoint = '%s%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIError):
            ThriftCLI._split_endpoint(endpoint)
        endpoint = '%s.%s.abc' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIError):
            ThriftCLI._split_endpoint(endpoint)
