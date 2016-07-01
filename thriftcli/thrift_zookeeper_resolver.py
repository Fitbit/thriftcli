import json
import os
import random
import urlparse

from kazoo.client import KazooClient

from .thrift_cli_error import ThriftCLIError


def get_server_address(zookeeper_address, service_name):
    """ Extracts the server address from a zookeeper address for a given service. """
    if '//' not in zookeeper_address:
        zookeeper_address = '//' + zookeeper_address
    url_obj = urlparse.urlparse(zookeeper_address)
    host = '%s:%s' % (url_obj.hostname, url_obj.port)
    znode = _get_znode_from_zookeeper_host(host, url_obj.path)
    return _parse_znode_for_address(znode, service_name, url_obj.path)


def _get_znode_from_zookeeper_host(host, path):
    """ Picks a znode assigned to a path. """
    zk = KazooClient(hosts=host)
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
    """ Extracts the hostname and port for the providing server from the znode. """
    data = json.loads(znode[0])
    try:
        address = data['additionalEndpoints'][service_name]
    except KeyError:
        raise ThriftCLIError('\'%s\' service not provided by \'%s\'' % (service_name, path))
    hostname, port = address['host'], address['port']
    address = '%s:%s' % (hostname, port)
    return address
