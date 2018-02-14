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
import subprocess
import sys
import urlparse

from thrift.transport import TSocket
from thrift.transport import TTransport
from twitter.common.rpc.finagle.protocol import TFinagleProtocol

from .thrift_cli_error import ThriftCLIError


class ThriftExecutor(object):
    """ This class handles connecting to and communicating with the Thrift server. """

    def __init__(self, server_address, service_name, thrift_loader, client_id=None):
        """ Opens a connection with the server and generates then imports the thrift-defined python code.

        :param server_address: the address to the server implementing the service
        :param client_id: Finagle client id for identifying requests

        """
        self._server_address = server_address
        self._service_name = service_name
        self._thrift_loader = thrift_loader

        self._client_id = client_id
        self._open_connection(server_address)

    def run(self, method_name, request_args):
        """ Executes a method on the connected server and returns its result.

        :param method_name: the name of the method to call
        :type method_name: str
        :param request_args: keyword arguments to pass into method call, acting as a request body
        :type request_args: dict
        :return: the result of the method call

        """
        method = self._thrift_loader.get_client_method(service_name, method_name)
        return method(**request_args)

    def cleanup(self, remove_generated_src=False):
        """ Deletes the gen-py code and closes the transport with the server.

        :param remove_generated_src: whether or not to delete the generated source

        """
        self._thrift_loader.cleanup(remove_generated_src)
        if self._transport:
            self._transport.close()

    def _open_connection(self, address):
        """ Opens a connection with a server address.

        :param address: the address of the server to connect to

        """
        (url, port) = self._parse_address_for_hostname_and_port(address)
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

