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
import os
import random
import urlparse

from kazoo.client import KazooClient

from .thrift_cli_error import ThriftCLIError


def get_server_address(zk_host_address, service_name):
    """ Extracts the server address from a zookeeper address for a given service.

    :param zk_host_address: the address of the Zookeeper host, as given as a command line argument
    :param service_name: the name of the service interface being requested
    :returns: the address of a server implementing the desired service
    :rtype: str

    """
    if '//' not in zk_host_address:
        zk_host_address = '//' + zk_host_address
    url_obj = urlparse.urlparse(zk_host_address)
    zk_host_address = '%s:%s' % (url_obj.hostname, url_obj.port)
    znode = _get_znode_from_zookeeper_host(zk_host_address, url_obj.path)
    return _parse_znode_for_address(znode, service_name, url_obj.path)


def _get_znode_from_zookeeper_host(zk_host_address, path):
    """ Picks a znode assigned to a path.

    :param zk_host_address: the address of the Zookeeper host
    :param path: the path to the server set as registered under Zookeeper
    :returns: a random node from the host's server set for the given path
    :rtype: Znode

    """
    zk = KazooClient(hosts=zk_host_address)
    zk.start()
    children = zk.get_children(path)
    try:
        child = random.choice(children)
    except IndexError:
        raise ThriftCLIError('Path not found on Zookeeper: \'%s\'' % path)
    znode = zk.get(os.path.join(path, child))
    zk.stop()
    return znode


def _parse_znode_for_address(znode, service_name, path):
    """ Extracts the hostname and port for the providing server from the znode.

    :param znode: the znode object returned by Zookeeper
    :param service_name: the name of the service interface implemented by the znode
    :param path: the path to the server set as registered under Zookeeper
    :returns: the address of a server implementing the desired service
    :rtype: str

    """
    data = json.loads(znode[0])
    try:
        address = data['additionalEndpoints'][service_name]
    except KeyError:
        raise ThriftCLIError('\'%s\' service not provided by \'%s\'' % (service_name, path))
    hostname, port = address['host'], address['port']
    address = '%s:%s' % (hostname, port)
    return address
