import shutil
import subprocess
import sys
import urlparse
import random
import os
import json

from kazoo.client import KazooClient

from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket
from thrift.transport import TTransport

from .thrift_cli_error import ThriftCLIError
from .thrift_parser import ThriftParser


class ThriftExecutor(object):
    def __init__(self, thrift_path, server_address, thrift_dir_paths=None, zookeeper=False):
        """ Opens a connection with the server and generates then imports the thrift-defined python code. """
        self._thrift_path = thrift_path
        self._server_address = server_address
        self._thrift_dir_paths = thrift_dir_paths if thrift_dir_paths is not None else []
        self._open_connection(self._server_address, zookeeper)
        self._generate_and_import_packages()

    def run(self, service_reference, method_name, request_args):
        """ Executes a method on the connected server and returns its result.

        :param service_reference: Reference to the service implementing the desired method to call.
        :type service_reference: str
        :param method_name: Name of the method to call.
        :type method_name: str
        :param request_args: Keyword arguments to pass into method call, acting as a request body.
        :type request_args: dict
        :return: Result of method call.

        """
        method = self._get_method_from_endpoint(service_reference, method_name)
        return method(**request_args)

    def cleanup(self, remove_generated_src=False):
        """ Deletes the gen-py code and closes the transport with the server. """
        if remove_generated_src:
            self._remove_dir('gen-py')
        if self._transport:
            self._transport.close()

    @staticmethod
    def _remove_dir(path):
        """ Removes a directory and ignores if it didn't exist. """
        try:
            shutil.rmtree(path)
        except OSError:
            pass

    def _generate_and_import_packages(self):
        """ Generates and imports the python modules defined by the thrift code. """
        thrift_dir_options = ''.join([' -I %s' % thrift_dir_path for thrift_dir_path in self._thrift_dir_paths])
        command = 'thrift -r%s --gen py %s' % (thrift_dir_options, self._thrift_path)
        if subprocess.call(command, shell=True):
            raise ThriftCLIError('Thrift generation command failed: \'%s\'' % command)
        sys.path.append('gen-py')
        self._import_package(ThriftParser.get_package_name(self._thrift_path))

    def _get_method_from_endpoint(self, service_reference, method_name):
        """ Returns the python method generated for the given endpoint. """
        class_name = 'Client'
        client_constructor = getattr(sys.modules[service_reference], class_name)
        client = client_constructor(self._protocol)
        try:
            method = getattr(client, method_name)
        except AttributeError:
            raise ThriftCLIError('\'%s\' service has no method \'%s\'' % (service_reference, method_name))
        return method

    def _open_connection(self, address, zookeeper=False):
        """ Opens a connection with a server address. """
        (url, port) = self._parse_address_for_hostname_and_port(address, zookeeper)
        self._transport = TSocket.TSocket(url, port)
        self._transport = TTransport.TFramedTransport(self._transport)
        self._protocol = TBinaryProtocol.TBinaryProtocol(self._transport)
        self._transport.open()

    @staticmethod
    def _parse_address_for_hostname_and_port(address, zookeeper=False):
        """ Extracts the hostname and port from a url address. """
        if zookeeper:
            return ThriftExecutor._parse_zookeeper_address_for_hostname_and_port(address)
        if '//' not in address:
            address = '//' + address
        url_obj = urlparse.urlparse(address)
        return url_obj.hostname, url_obj.port

    @staticmethod
    def _parse_zookeeper_address_for_hostname_and_port(address):
        """ Extracts the hostname and port from a zookeeper address. """
        if '//' not in address:
            address = '//' + address
        url_obj = urlparse.urlparse(address)
        host = '%s:%s' % (url_obj.hostname, url_obj.port)
        znode = ThriftExecutor._get_znode_from_zookeeper_host(host, url_obj.path)
        return ThriftExecutor._parse_znode_for_hostname_and_port(znode)

    @staticmethod
    def _get_znode_from_zookeeper_host(host, path):
        """ Picks a znode assigned to a path. """
        zk = KazooClient(hosts=host)
        zk.start()
        children = zk.get_children(path)
        child = random.choice(children)
        znode = zk.get(os.path.join(path, child))
        zk.stop()
        return znode

    @staticmethod
    def _parse_znode_for_hostname_and_port(znode):
        """ Extracts the hostname and port from the znode. """
        data = json.loads(znode[0])
        address = data['serviceEndpoint']
        hostname, port = address['host'], address['port']
        return hostname, port

    @staticmethod
    def _import_package(package_name):
        """ Imports a package generated by thrift code. """
        package = __import__(package_name, globals())
        modules = package.__all__
        for module in modules:
            module_name = '.'.join([package_name, module])
            __import__(module_name, globals())
