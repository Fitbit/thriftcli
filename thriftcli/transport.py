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

"""For those times you want to access your TSocket transport service via a proxy.

Maybe you need to access some backend services via a squid proxy that uses kerberos for authentication, authorization
and auditing ofthese requests.

TProxySocket is a thin wrapper around TSocket transport that uses httplib to handle setting up the tunnel 
and requests_kerberos to handle kerberos auth.
"""
import httplib
import requests_kerberos
import socket

from thrift.transport import TSocket
from thrift.transport import TTransport

class TProxySocket(TSocket.TSocket):
  """Thrift transport, adds proxy support to TSocket transport."""
  def __init__(self, proxy_host=None, proxy_port=None, *args, **kwargs):
    if proxy_host is None and proxy_port is None:
      return TSocket.TSocket(*args, **kwargs)

    TSocket.TSocket.__init__(self, *args, **kwargs)
    self.proxy_host = proxy_host
    self.proxy_port = proxy_port

  def open(self):
    """Open a connection.

    This is mostly copy pasta from thrift.transport.TSocket.open, but adds call to _setup_tunnel().
    """
    try:
      res0 = self._resolveAddr()
      for res in res0:
        try:
          self.handle = self._setup_tunnel(res[4])
          self.handle.settimeout(self._timeout)
        except socket.error as e:
          if res is not res0[-1]:
            continue
          else:
            raise e
        break
    except socket.error as e:
      if self._unix_socket:
        message = 'Could not connect to socket %s' % self._unix_socket
      else:
        message = 'Could not connect to %s:%d' % (self.host, self.port)
      raise TTransport.TTransportException(type=TTransport.TTransportException.NOT_OPEN,
                                message=message)

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


