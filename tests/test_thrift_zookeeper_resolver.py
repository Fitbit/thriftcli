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

import unittest

import mock

from tests import data
from thriftcli import ThriftCLIError
from thriftcli.thrift_zookeeper_resolver import get_server_address, _get_znode_from_zookeeper_host


class TestThriftZookeeperResolver(unittest.TestCase):
    @mock.patch('thriftcli.thrift_zookeeper_resolver._get_znode_from_zookeeper_host')
    def test_get_server_address(self, mock_get_znode):
        mock_get_znode.return_value = data.TEST_ZNODE
        address = get_server_address(data.TEST_ZOOKEEPER_SERVER_ADDRESS, data.TEST_THRIFT_SERVICE_NAME)
        expected_address = '%s:%s' % (data.TEST_SERVER_HOSTNAME2, data.TEST_SERVER_PORT2)
        self.assertEqual(address, expected_address)

    @mock.patch('thriftcli.thrift_zookeeper_resolver._get_znode_from_zookeeper_host')
    def test_get_server_address_invalid_service(self, mock_get_znode):
        mock_get_znode.return_value = data.TEST_ZNODE
        with self.assertRaises(ThriftCLIError):
            get_server_address(data.TEST_ZOOKEEPER_SERVER_ADDRESS, data.TEST_THRIFT_SERVICE_NAME2)

    @mock.patch('kazoo.client.KazooClient.stop')
    @mock.patch('kazoo.client.KazooClient.get')
    @mock.patch('kazoo.client.KazooClient.get_children')
    @mock.patch('kazoo.client.KazooClient.start')
    def test_get_znode_from_zookeeper_host(self, mock_start, mock_get_children, mock_get, mock_stop):
        mock_get_children.return_value = [data.TEST_ZOOKEEPER_CHILD_NAME]
        mock_get.return_value = data.TEST_ZNODE
        znode = _get_znode_from_zookeeper_host(data.TEST_SERVER_ADDRESS, data.TEST_ZOOKEEPER_PATH)
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
            _get_znode_from_zookeeper_host(data.TEST_SERVER_ADDRESS, data.TEST_ZOOKEEPER_PATH)
