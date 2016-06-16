import unittest

import mock

import data
from thriftcli import ThriftCLI, ThriftCLIException


class TestThriftCLI(unittest.TestCase):
    @mock.patch('thriftcli.ThriftCLI._open_connection')
    @mock.patch('thriftcli.ThriftCLI._import_module')
    @mock.patch('subprocess.call')
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_setup(self, mock_load_file, mock_call, mock_import_module, mock_open_connection):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        mock_call.side_effect = None
        cli = ThriftCLI()
        cli.setup(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS)
        command = 'thrift -r --gen py %s' % data.TEST_THRIFT_PATH
        mock_call.assert_called_with(command, shell=True)
        mock_import_module.assert_called_with(data.TEST_THRIFT_MODULE_NAME)
        mock_open_connection.assert_called_with(data.TEST_SERVER_ADDRESS)

    @mock.patch('thriftcli.TSocket.TSocket')
    @mock.patch('thriftcli.ThriftCLI._import_module')
    @mock.patch('subprocess.call')
    @mock.patch('thriftcli.ThriftParser._load_file')
    @mock.patch('thriftcli.ThriftCLI._remove_dir')
    def test_cleanup(self, mock_remove_dir, mock_load_file, mock_call, mock_import_module, mock_tsocket):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        mock_import_module.side_effect = None
        mock_call.side_effect = None
        mock_remove_dir.side_effect = None
        mock_tsocket.side_effect = None
        cli = ThriftCLI()
        cli.setup(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS)
        cli.cleanup()
        expected_rm_path = 'gen-py'
        command = 'thrift -r --gen py %s' % data.TEST_THRIFT_PATH
        mock_call.assert_called_with(command, shell=True)
        self.assertTrue(mock_remove_dir.called)
        mock_remove_dir.assert_called_with(expected_rm_path)

    def test_get_module_name(self):
        expected_module_name = data.TEST_THRIFT_MODULE_NAME
        module_name = ThriftCLI.get_module_name(data.TEST_THRIFT_PATH)
        self.assertEqual(module_name, expected_module_name)

    def test_split_endpoint(self):
        cli = ThriftCLI()
        endpoint = '%s.%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        expected_service_name, expected_method_name = data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME
        service_name, method_name = cli._split_endpoint(endpoint)
        self.assertEqual((service_name, method_name), (expected_service_name, expected_method_name))
        endpoint = '%s%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIException):
            cli._split_endpoint(endpoint)
        endpoint = '%s.%s.abc' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIException):
            cli._split_endpoint(endpoint)

    @mock.patch('thriftcli.TTransport.TBufferedTransport.open')
    @mock.patch('thriftcli.TSocket.TSocket')
    def test_open_connection(self, mock_tsocket, mock_transport_open):
        cli = ThriftCLI()
        cli._open_connection(data.TEST_SERVER_ADDRESS)
        mock_tsocket.assert_called_with(data.TEST_SERVER_HOSTNAME, data.TEST_SERVER_PORT)
        self.assertTrue(mock_transport_open.called)

    def test_parse_address_for_hostname_and_url(self):
        hostname, port = ThriftCLI._parse_address_for_hostname_and_port(data.TEST_SERVER_ADDRESS)
        hostname2, port2 = ThriftCLI._parse_address_for_hostname_and_port(data.TEST_SERVER_ADDRESS2)
        hostname3, port3 = ThriftCLI._parse_address_for_hostname_and_port(data.TEST_SERVER_ADDRESS3)
        expected_hostname, expected_port = data.TEST_SERVER_HOSTNAME, data.TEST_SERVER_PORT
        expected_hostname2, expected_port2 = data.TEST_SERVER_HOSTNAME2, data.TEST_SERVER_PORT2
        expected_hostname3, expected_port3 = data.TEST_SERVER_HOSTNAME3, data.TEST_SERVER_PORT3
        self.assertEqual((hostname, port), (expected_hostname, expected_port))
        self.assertEqual((hostname2, port2), (expected_hostname2, expected_port2))
        self.assertEqual((hostname3, port3), (expected_hostname3, expected_port3))

    # @mock.patch('thriftcli.TSocket.TSocket')
    # @mock.patch('thriftcli.ThriftParser._load_file')
    # def test_convert_json_to_args(self, mock_load_file, mock_tsocket):
    #     mock_load_file.return_value = data.TEST_THRIFT_CONTENT
    #     mock_tsocket.side_effect = None
    #     cli = ThriftCLI()
    #     try:
    #         cli.setup(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS)
    #         cli._endpoint = data.TEST_THRIFT_ENDPOINT_NAME
    #         request_args = cli._convert_json_to_args(
    #             data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME, data.TEST_REQUEST_JSON)
    #         expected_request_args = data.TEST_REQUEST_ARGS
    #         self.assertEqual(request_args, expected_request_args)
    #     finally:
    #         cli.cleanup()

    def test_calc_map_types_split_index(self):
        test_map_type = 'string, string'
        expected_split_index = len('string')
        split_index = ThriftCLI.calc_map_types_split_index(test_map_type)
        self.assertEqual(split_index, expected_split_index)
        test_map_type = 'map<string, list<i32>>, set<string>'
        expected_split_index = len('map<string, list<i32>>')
        split_index = ThriftCLI.calc_map_types_split_index(test_map_type)
        self.assertEqual(split_index, expected_split_index)
