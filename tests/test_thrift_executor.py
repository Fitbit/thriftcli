import unittest

import mock

import data
from thriftcli import ThriftExecutor, ThriftCLIError


class TestThriftExecutor(unittest.TestCase):
    @mock.patch('thriftcli.TTransport.TFramedTransport.open')
    @mock.patch('thriftcli.TSocket.TSocket')
    @mock.patch('thriftcli.ThriftExecutor._import_package')
    @mock.patch('subprocess.call')
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_init(self, mock_load_file, mock_call, mock_import_package, mock_tsocket, mock_transport_open):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        mock_call.return_value = 0
        ThriftExecutor(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS, data.TEST_THRIFT_SERVICE_REFERENCE)
        command = 'thrift -r --gen py %s' % data.TEST_THRIFT_PATH
        mock_call.assert_called_with(command, shell=True)
        mock_import_package.assert_called_with(data.TEST_THRIFT_MODULE_NAME)
        mock_tsocket.assert_called_with(data.TEST_SERVER_HOSTNAME, data.TEST_SERVER_PORT)
        self.assertTrue(mock_transport_open.called)

    def test_parse_address_for_hostname_and_url(self):
        hostname, port = ThriftExecutor._parse_address_for_hostname_and_port(data.TEST_SERVER_ADDRESS)
        hostname2, port2 = ThriftExecutor._parse_address_for_hostname_and_port(data.TEST_SERVER_ADDRESS2)
        hostname3, port3 = ThriftExecutor._parse_address_for_hostname_and_port(data.TEST_SERVER_ADDRESS3)
        expected_hostname, expected_port = data.TEST_SERVER_HOSTNAME, data.TEST_SERVER_PORT
        expected_hostname2, expected_port2 = data.TEST_SERVER_HOSTNAME2, data.TEST_SERVER_PORT2
        expected_hostname3, expected_port3 = data.TEST_SERVER_HOSTNAME3, data.TEST_SERVER_PORT3
        self.assertEqual((hostname, port), (expected_hostname, expected_port))
        self.assertEqual((hostname2, port2), (expected_hostname2, expected_port2))
        self.assertEqual((hostname3, port3), (expected_hostname3, expected_port3))

    @mock.patch('thriftcli.ThriftExecutor._get_znode_from_zookeeper_host')
    def test_parse_address_for_hostname_and_url_for_zookeeper(self, mock_get_znode):
        mock_get_znode.return_value = data.TEST_ZNODE
        hostname, port = ThriftExecutor._parse_address_for_hostname_and_port(
            data.TEST_ZOOKEEPER_SERVER_ADDRESS,
            zookeeper=True,
            service_name=data.TEST_THRIFT_SERVICE_NAME)
        expected_hostname, expected_port = data.TEST_SERVER_HOSTNAME2, data.TEST_SERVER_PORT2
        self.assertEqual((hostname, port), (expected_hostname, expected_port))

    @mock.patch('kazoo.client.KazooClient.stop')
    @mock.patch('kazoo.client.KazooClient.get')
    @mock.patch('kazoo.client.KazooClient.get_children')
    @mock.patch('kazoo.client.KazooClient.start')
    def test_get_znode_from_zookeeper_host(self, mock_start, mock_get_children, mock_get, mock_stop):
        mock_get_children.return_value = [data.TEST_ZOOKEEPER_CHILD_NAME]
        mock_get.return_value = data.TEST_ZNODE
        znode = ThriftExecutor._get_znode_from_zookeeper_host(data.TEST_SERVER_ADDRESS, data.TEST_ZOOKEEPER_PATH)
        expected_znode = data.TEST_ZNODE
        self.assertEqual(znode, expected_znode)
        self.assertTrue(mock_start.called)
        mock_get_children.assert_called_with(data.TEST_ZOOKEEPER_PATH)
        mock_get.assert_called_with(data.TEST_ZOOKEEPER_CHILD_PATH)
        self.assertTrue(mock_stop.called)

    def test_split_service_reference(self):
        reference = '%s.%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        expected_service_name, expected_method_name = data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME
        service_name, method_name = ThriftExecutor._split_service_reference(reference)
        self.assertEqual((service_name, method_name), (expected_service_name, expected_method_name))
        reference = '%s%s' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIError):
            ThriftExecutor._split_service_reference(reference)
        reference = '%s.%s.abc' % (data.TEST_THRIFT_SERVICE_NAME, data.TEST_THRIFT_METHOD_NAME)
        with self.assertRaises(ThriftCLIError):
            ThriftExecutor._split_service_reference(reference)
