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
    def __init__(self, thrift_path, server_address, service_reference, thrift_dir_paths=None, zookeeper=False):
        """ Opens a connection with the server and generates then imports the thrift-defined python code. """
        self._thrift_path = thrift_path
        self._server_address = server_address
        self._thrift_dir_paths = thrift_dir_paths if thrift_dir_paths is not None else []
        self._service_reference = service_reference
        service_name = ThriftExecutor._split_service_reference(service_reference)[1]
        self._open_connection(server_address, zookeeper, service_name)
        self._generate_and_import_packages()

    def run(self, method_name, request_args):
        """ Executes a method on the connected server and returns its result.

        :param method_name: Name of the method to call.
        :type method_name: str
        :param request_args: Keyword arguments to pass into method call, acting as a request body.
        :type request_args: dict
        :return: Result of method call.

        """
        method = self._get_method(method_name)
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

    def _get_method(self, method_name):
        """ Returns the python method generated for the given endpoint. """
        class_name = 'Client'
        client_constructor = getattr(sys.modules[self._service_reference], class_name)
        client = client_constructor(self._protocol)
        try:
            method = getattr(client, method_name)
        except AttributeError:
            raise ThriftCLIError('\'%s\' service has no method \'%s\'' % (self._service_reference, method_name))
        return method

    def _open_connection(self, address, zookeeper=False, service_name=None):
        """ Opens a connection with a server address. """
        (url, port) = self._parse_address_for_hostname_and_port(address, zookeeper, service_name)
        self._transport = TSocket.TSocket(url, port)
        self._transport = TTransport.TFramedTransport(self._transport)
        self._protocol = TBinaryProtocol.TBinaryProtocol(self._transport)
        self._transport.open()

    @staticmethod
    def _parse_address_for_hostname_and_port(address, zookeeper=False, service_name=None):
        """ Extracts the hostname and port from a url address. """
        if zookeeper:
            return ThriftExecutor._parse_zookeeper_address_for_hostname_and_port(address, service_name)
        if '//' not in address:
            address = '//' + address
        url_obj = urlparse.urlparse(address)
        return url_obj.hostname, url_obj.port

    @staticmethod
    def _parse_zookeeper_address_for_hostname_and_port(address, service_name):
        """ Extracts the hostname and port from a zookeeper address. """
        if '//' not in address:
            address = '//' + address
        url_obj = urlparse.urlparse(address)
        host = '%s:%s' % (url_obj.hostname, url_obj.port)
        znode = ThriftExecutor._get_znode_from_zookeeper_host(host, url_obj.path)
        return ThriftExecutor._parse_znode_for_hostname_and_port(znode, service_name, url_obj.path)

    @staticmethod
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

    @staticmethod
    def _parse_znode_for_hostname_and_port(znode, service_name, path):
        """ Extracts the hostname and port for the providing server from the znode. """
        data = json.loads(znode[0])
        try:
            address = data['additionalEndpoints'][service_name]
        except KeyError:
            raise ThriftCLIError('\'%s\' service not provided by \'%s\'' % (service_name, path))
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

    @staticmethod
    def _split_service_reference(reference):
        """ Extracts the package name and service name from a service reference. """
        split = reference.split('.')
        if not split or len(split) != 2:
            raise ThriftCLIError('Service reference should be in format \'package.Service\', given: \'%s\'' % reference)
        return split
