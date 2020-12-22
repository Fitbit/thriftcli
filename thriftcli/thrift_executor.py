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

import importlib
import os
import shutil
import ssl
import subprocess
import sys
import urlparse

from thrift.transport import TSSLSocket
from thrift.transport import TSocket
from thrift.transport import TTransport
from twitter.common.rpc.finagle.protocol import TFinagleProtocol

from tls_transport import TProxySSLSocket
from .thrift_cli_error import ThriftCLIError
from .transport import TProxySocket


class ThriftExecutor(object):
    """ This class handles connecting to and communicating with the Thrift server. """

    def __init__(self, thrift_path, server_address, service_reference, basename_to_namespaces,
                 tls=False, tls_key_path=None, cert_verification_mode=None,
                 thrift_dir_paths=None,
                 client_id=None, proxy=None):
        """ Opens a connection with the server and generates then imports the thrift-defined python code.

        :param thrift_path: the path to the Thrift file defining the service being requested
        :param server_address: the address to the server implementing the service
        :param service_reference: the namespaced service name in the format <file-name>.<service-name>
        :param thrift_dir_paths: a list of paths to directories containing Thrift file dependencies
        :param client_id: Finagle client id for identifying requests
        :param proxy: [<proxy host>:<proxy port>] to route request through
        """
        self._thrift_path = thrift_path
        self._server_address = server_address

        self._thrift_dir_paths = set(thrift_dir_paths) if thrift_dir_paths is not None else set([])
        # Handle case where thrift file is in the current directory
        thrift_file_dir = os.path.dirname(thrift_path) or '.'
        self._thrift_dir_paths.add(thrift_file_dir)

        self._client_id = client_id
        self._service_reference = service_reference
        self._proxy = proxy
        self._tls = tls
        self._tls_key_path = tls_key_path
        self.cert_verification_mode = cert_verification_mode
        self._open_connection(server_address)
        self._generate_and_import_packages(basename_to_namespaces)

    def run(self, method_name, request_args):
        """ Executes a method on the connected server and returns its result.

        :param method_name: the name of the method to call
        :type method_name: str
        :param request_args: keyword arguments to pass into method call, acting as a request body
        :type request_args: dict
        :return: the result of the method call

        """
        method = self._get_method(method_name)
        return method(**request_args)

    def cleanup(self, remove_generated_src=False):
        """ Deletes the gen-py code and closes the transport with the server.

        :param remove_generated_src: whether or not to delete the generated source

        """
        if remove_generated_src:
            self._remove_dir('gen-py')
        if self._transport:
            self._transport.close()

    @staticmethod
    def _remove_dir(path):
        """ Recursively removes a directory and ignores if it didn't exist.

        :param path: the directory to remove

        """
        try:
            shutil.rmtree(path)
        except OSError:
            pass

    def _generate_and_import_packages(self, basename_to_namespaces):
        """ Generates and imports the python modules defined by the thrift code.

        This method does the following:
        1. Runs a shell process to generate the python code from the Thrift file
        2. Adds the generated source to the python process' path
        3. Imports the generated source package into this python process

        """
        thrift_dir_options = ''.join([' -I %s' % thrift_dir_path for thrift_dir_path in self._thrift_dir_paths])
        command = 'thrift -r%s --gen py %s' % (thrift_dir_options, self._thrift_path)
        if subprocess.call(command, shell=True) != 0:
            raise ThriftCLIError('Thrift generation command failed: \'%s\'' % command)
        sys.path.append('gen-py')
        for basename, package in basename_to_namespaces.items():
            self._import_package(basename, package)

    def _get_method(self, method_name):
        """ Returns the python method generated for the given endpoint.

        :param method_name: the name of the method to retrieve
        :returns: the python method that can be called to execute the Thrift RPC
        :rtype: method

        """
        class_name = 'Client'
        client_constructor = getattr(sys.modules[self._service_reference], class_name)
        client = client_constructor(self._protocol)
        try:
            method = getattr(client, method_name)
        except AttributeError:
            raise ThriftCLIError('\'%s\' service has no method \'%s\'' % (self._service_reference, method_name))
        return method

    def _open_connection(self, address):
        """ Opens a connection with a server address.

        :param address: the address of the server to connect to

        """
        (url, port) = self._parse_address_for_hostname_and_port(address)
        if self._tls:
            verifier_type = self._get_verifier_type(self.cert_verification_mode)
            if self._proxy:
                proxy_host, proxy_port = self._proxy.split(":")
                self._transport = TProxySSLSocket(url, port, proxy_host, proxy_port, verifier_type, ca_certs=self._tls_key_path)
            else:
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
                if self._tls_key_path is not None:
                    ssl_context.load_cert_chain(self._tls_key_path, self._tls_key_path)
                ssl_context.verify_mode = verifier_type
                self._transport = TSSLSocket.TSSLSocket(url, port, ca_certs=self._tls_key_path,
                                                        validate_callback=lambda cert, hostname: None)  # disabling hostname validation
        else:
            if self._proxy:
                proxy_host, proxy_port = self._proxy.split(":")
                self._transport = TProxySocket(proxy_host, proxy_port, url, port)
            else:
                self._transport = TSocket.TSocket(url, port)
        self._transport = TTransport.TFramedTransport(self._transport)
        self._transport.open()
        self._protocol = TFinagleProtocol(self._transport, client_id=self._client_id)

    @staticmethod
    def _parse_address_for_hostname_and_port(address):
        """ Extracts the hostname and port from a url address.

        :param address: an address to parse
        :returns: the hostname and port of the address
        :rtype: tuple of (str, str)

        """
        if '//' not in address:
            address = '//' + address
        url_obj = urlparse.urlparse(address)
        return url_obj.hostname, url_obj.port

    @staticmethod
    def _import_package(basename, package_name):
        """ Imports a package generated by thrift code

        :param package_name: the name of the package to import, which must be located somewhere on sys.path

        """
        package = importlib.import_module(package_name)
        for module in package.__all__:
            sub_module_name = '.'.join([basename, module])
            sub_package_name = '.'.join([package_name, module])
            sub_package = importlib.import_module(sub_package_name)
            sys.modules[sub_module_name] = sub_package

    @staticmethod
    def _get_verifier_type(cert_verification_mode):
        """ Maps string value to SSL certificate verification type. Can be 'none', 'optional', 'required'.

        :param cert_verification_mode: string representation of verification mode.
        :returns: numeric code of verification mode
        """
        modes = {
            'none': ssl.CERT_NONE,
            'optional': ssl.CERT_OPTIONAL,
            'required': ssl.CERT_REQUIRED
        }
        if cert_verification_mode in modes:
            return modes[cert_verification_mode]
        else:
            raise ValueError('Unknown certificate verification mode: {}'.format(cert_verification_mode))
