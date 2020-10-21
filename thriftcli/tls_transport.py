# Copyright Notice:
# Copyright 2020, Fitbit, Inc.
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import httplib
import os
import socket
import ssl

import requests_kerberos
from thrift.transport import TSocket
from thrift.transport.TTransport import TTransportException


class TProxySSLSocket(TSocket.TSocket):
    SSL_VERSION = ssl.PROTOCOL_SSLv23

    def __init__(self, host, port, proxy_host, proxy_port,
                 cert_verification_mode,
                 ca_certs=None,
                 unix_socket=None):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.is_valid = False
        self.cert_reqs = cert_verification_mode
        self.ca_certs = ca_certs
        if ca_certs is not None and not os.access(ca_certs, os.R_OK):
            raise IOError(
                'Certificate Authority ca_certs file "%s" is not readable, cannot validate SSL certificates.' % (ca_certs))
        TSocket.TSocket.__init__(self, host, port, unix_socket)

    def open(self):
        try:
            addrs = self._resolveAddr()
            for res in addrs:
                ip_port = res[4]
                plain_sock = self._setup_tunnel(ip_port)
                plain_sock.settimeout(self._timeout)
                self.handle = ssl.wrap_socket(plain_sock, certfile=self.ca_certs, ssl_version=ssl.PROTOCOL_TLSv1_2)
                self.handle.settimeout(self._timeout)
        except socket.error, e:
            if self._unix_socket:
                message = 'Could not connect to secure socket %s' % self._unix_socket
            else:
                message = 'Could not connect to %s:%d' % (self.host, self.port)
            raise TTransportException(type=TTransportException.NOT_OPEN, message=message)

    def _setup_tunnel(self, host_port):
        """Use HTTPConnection to HTTP CONNECT to our proxy, connect to the backend and return socket for this tunnel.

        host_port: tuple (host, port) from thrift.transport.TSocket._resolveAddr.
        """
        conn = httplib.HTTPConnection(self.proxy_host, self.proxy_port)
        auth_header = requests_kerberos.HTTPKerberosAuth().generate_request_header(None,
                                                                                   self.proxy_host,
                                                                                   is_preemptive=True)
        conn.set_tunnel(
            *host_port,
            headers={'Proxy-Authorization': auth_header})
        conn.connect()
        return conn.sock
