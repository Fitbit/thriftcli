import mock
import unittest
import data

from thriftcli import ThriftZookeeperResolver, ThriftCLIError


class TestThriftZookeeperResolver(unittest.TestCase):

    @mock.patch('thriftcli.ThriftZookeeperResolver._get_znode_from_zookeeper_host')
    def test_get_server_address(self, mock_get_znode):
        mock_get_znode.return_value = data.TEST_ZNODE
        address = ThriftZookeeperResolver.get_server_address(
            data.TEST_ZOOKEEPER_SERVER_ADDRESS,
            data.TEST_THRIFT_SERVICE_NAME)
        expected_address = '%s:%s' % (data.TEST_SERVER_HOSTNAME2, data.TEST_SERVER_PORT2)
        self.assertEqual(address, expected_address)

    @mock.patch('thriftcli.ThriftZookeeperResolver._get_znode_from_zookeeper_host')
    def test_get_server_address_invalid_service(self, mock_get_znode):
        mock_get_znode.return_value = data.TEST_ZNODE
        with self.assertRaises(ThriftCLIError):
            ThriftZookeeperResolver.get_server_address(
                data.TEST_ZOOKEEPER_SERVER_ADDRESS,
                data.TEST_THRIFT_SERVICE_NAME2)

    @mock.patch('kazoo.client.KazooClient.stop')
    @mock.patch('kazoo.client.KazooClient.get')
    @mock.patch('kazoo.client.KazooClient.get_children')
    @mock.patch('kazoo.client.KazooClient.start')
    def test_get_znode_from_zookeeper_host(self, mock_start, mock_get_children, mock_get, mock_stop):
        mock_get_children.return_value = [data.TEST_ZOOKEEPER_CHILD_NAME]
        mock_get.return_value = data.TEST_ZNODE
        znode = ThriftZookeeperResolver._get_znode_from_zookeeper_host(
            data.TEST_SERVER_ADDRESS,
            data.TEST_ZOOKEEPER_PATH)
        expected_znode = data.TEST_ZNODE
        self.assertEqual(znode, expected_znode)
        self.assertTrue(mock_start.called)
        mock_get_children.assert_called_with(data.TEST_ZOOKEEPER_PATH)
        mock_get.assert_called_with(data.TEST_ZOOKEEPER_CHILD_PATH)
        self.assertTrue(mock_stop.called)

    @mock.patch('kazoo.client.KazooClient.stop')
    @mock.patch('kazoo.client.KazooClient.get_children')
    @mock.patch('kazoo.client.KazooClient.start')
    def test_get_znode_from_zookeeper_host_invalid_path(self, mock_start, mock_get_children, mock_stop):
        mock_start.side_effect = None
        mock_stop.side_effect = None
        mock_get_children.return_value = []
        with self.assertRaises(ThriftCLIError):
            ThriftZookeeperResolver._get_znode_from_zookeeper_host(
                data.TEST_SERVER_ADDRESS,
                data.TEST_ZOOKEEPER_PATH)