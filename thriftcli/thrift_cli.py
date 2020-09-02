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

import argparse
import json
import logging
import os

from thrift_zookeeper_resolver import get_server_address
from .request_body_converter import convert
from .thrift_argument_converter import ThriftArgumentConverter
from .thrift_cli_error import ThriftCLIError
from .thrift_executor import ThriftExecutor
from .thrift_parser import ThriftParser

THRIFT_PATH_ENVIRONMENT_VARIABLE = 'THRIFT_CLI_PATH'


class ThriftCLI(object):
    """ Provides an interface for setting up a client, making requests, and cleaning up.

    Call init to open a connection with a server and inform ThriftCLI of the available endpoints.
    Call run to make a request.
    Call cleanup to close the connection and delete the generated python code.

    """

    def __init__(self, thrift_path, server_address, service_name, tls, tls_key_path, cert_verification_mode, thrift_dir_paths=None, zookeeper=False,
                 client_id=None,
                 proxy=None):
        """
        :param thrift_path: the path to the thrift file being used.
        :type thrift_path: str
        :param server_address: the address of the server to make requests to.
        :type server_address: str
        :param thrift_dir_paths: additional directories to search for included thrift files in.
        :type thrift_dir_paths: list of str
        :param zookeeper: whether or not to treat the server address as a zookeeper host with a path.
        :type zookeeper: bool
        :param client_id: Finagle client id for identifying requests
        :type client_id: str
        :param proxy: [<proxy host>:<proxy port>] to route request through
        :type proxy: str
        """
        self._thrift_path = _find_path(thrift_path)
        self._thrift_argument_converter = ThriftArgumentConverter(self._thrift_path, thrift_dir_paths)
        self._service_reference = '%s.%s' % (ThriftParser.get_package_name(self._thrift_path), service_name)
        if zookeeper:
            server_address = get_server_address(server_address, service_name)
        self._thrift_executor = ThriftExecutor(self._thrift_path, server_address, self._service_reference,
                                               self._thrift_argument_converter._parse_result.namespaces,
                                               tls, tls_key_path, cert_verification_mode,
                                               thrift_dir_paths=thrift_dir_paths, client_id=client_id, proxy=proxy)

    def run(self, method_name, request_body, return_json=False):
        """ Runs the endpoint on the connected server as defined by the thrift file.

        :param method_name: the name of the method to ask the server to run.
        :type method_name: str
        :param request_body: the arguments to provide as arguments to the endpoint.
        :type request_body: dict
        :param return_json: returns result in JSON format if True, python object if False.
        :type return_json: bool
        :returns: endpoint result

        """
        request_args = self._thrift_argument_converter.convert_args(self._service_reference, method_name, request_body)
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            logging.debug(
                "Performing Request %s",
                _dump_json(request_args)
            )
        result = self._thrift_executor.run(method_name, request_args)
        return self.transform_output(result, return_json)

    def cleanup(self, remove_generated_src=False):
        """ Deletes the gen-py code and closes the transport with the server. """
        self._thrift_executor.cleanup(remove_generated_src)

    @classmethod
    def transform_output(cls, result, return_json=False):
        if return_json:
            result = _dump_json(result)
        return result


def _dump_json(obj):
    return json.dumps(obj, default=_default_json_handler, sort_keys=True, indent=4, separators=(',', ': '))


def _default_json_handler(obj):
    if isinstance(obj, set) or isinstance(obj, frozenset):
        return list(obj)
    else:
        return obj.__dict__


def _find_path(path):
    if os.path.isfile(path):
        return path
    else:
        thrift_file = os.path.basename(path)
        for thrift_path in os.environ.get(THRIFT_PATH_ENVIRONMENT_VARIABLE, '').split(':'):
            try:
                if thrift_file in os.listdir(thrift_path):
                    return os.path.join(thrift_path, thrift_file)
            except OSError:
                # Dir did not contain file needed
                continue

    raise IOError("Unable to find {}".format(path))


def _split_endpoint(endpoint):
    """ Extracts the service name and method name from an endpoint.

    For example: "Service.function" -> ("Service", "function")

    :param endpoint: the endpoint reference being split
    :type endpoint: str
    :returns: a tuple of the service name and method name
    :rtype: tuple of (str, str)

    """
    split = endpoint.split('.')
    if not split or len(split) != 2:
        raise ThriftCLIError('Endpoint should be in format \'Service.function\', given: \'%s\'' % endpoint)
    return split


def _load_file(path):
    """ Returns the contents of a file.

    :param path: the file to open
    :type path: str
    :returns: the file contents
    :rtype: str

    """
    with open(path, 'r') as file_to_read:
        return file_to_read.read()


def _load_request_body(request_body_arg):
    """ Parses the request body argument into an argument dictionary.

    :param request_body_arg: either a file or a string containing the request body in some format
    :type request_body_arg: str
    :returns: the argument dictionary represented by the request body
    :rtype: dict

    """
    if not request_body_arg:
        return {}
    if os.path.isfile(request_body_arg):
        request_body_arg = _load_file(request_body_arg)
    try:
        return convert(request_body_arg)
    except ValueError, e:
        raise ThriftCLIError(e)


def _parse_namespace(args):
    """ Converts the namespace object returned by argparse into the desired variables.

    :param args: the namespace object given by the argparse library
    :type args: Namespace
    :returns: a tuple of all of the command line arguments
    :rtype: tuple

    """
    server_address = args.server_address
    endpoint = args.endpoint
    thrift_path = args.thrift_path
    thrift_dir_paths = args.include
    request_body = _load_request_body(args.body)
    zookeeper = args.zookeeper
    return_json = args.json
    cleanup = args.cleanup
    client_id = args.client_id
    proxy = args.proxy
    tls = args.tls
    tls_key_path = args.tls_key_path
    cert_verification_mode = args.cert_verification_mode
    return (server_address, endpoint, thrift_path, thrift_dir_paths, request_body, zookeeper, return_json, cleanup,
            client_id, proxy, tls, tls_key_path, cert_verification_mode)


def _make_parser():
    """ Initializes the ArgumentParser with all desired arguments.

    :returns: an ArgumentParser object configured for thriftcli
    :rtype: ArgumentParser

    """
    parser = argparse.ArgumentParser(description='Execute thrift endpoints on a running server.')
    parser.add_argument('server_address', type=str,
                        help='address of running server that implements the endpoint')
    parser.add_argument('endpoint', type=str,
                        help='name of endpoint, defined as Service.function')
    parser.add_argument('thrift_path', type=str,
                        help='path to thrift file declaring the endpoint')
    parser.add_argument('-I', '--include', type=str, nargs='*', default=[],
                        help='path to directory containing included thrift files')
    parser.add_argument('-b', '--body', type=str, nargs='?',
                        help='json string or path to json file encoding the request body')
    parser.add_argument('-z', '--zookeeper', action='store_true',
                        help='treat server address as a zookeeper host with a path')
    parser.add_argument('-p', '--proxy', type=str,
                        help='access the service via a proxy (for auth reasons) [<proxy host>:<proxy port>]')
    parser.add_argument('-c', '--cleanup', action='store_true',
                        help='remove generated code after execution')
    parser.add_argument('-j', '--json', action='store_true',
                        help='print result in JSON format')
    parser.add_argument('-i', '--client_id', type=str, default=None,
                        help='Finagle client id to send request with')
    parser.add_argument('-t', '--tls', action='store_true', help='Use TLS socket if provided')

    parser.add_argument('-k', '--tls_key_path', type=str,
                        help='path to tls key file. --tls key must be provided to enable mtls')
    parser.add_argument('-m', '--cert_verification_mode', type=str, default='required',
                        help='defines peer certificate verification mode. Possible values are none, optional, required. '
                             '--tls key must be provided to enable mtls')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='provide detailed logging')
    return parser


def _run_cli(server_address, endpoint_name, thrift_path, thrift_dir_paths, request_body, zookeeper, return_json,
             remove_generated_src, client_id, proxy, tls, tls_key_path, cert_verification_mode):
    """ Runs a remote request and prints the result if it is not None.

    :param server_address: the address of the Thrift server to request
    :type server_address: str
    :param endpoint_name: the name of the method to request
    :type endpoint_name: str
    :param thrift_path: the path to the Thrift file defining the service
    :type thrift_path: str
    :param thrift_dir_paths: a list of paths containing Thrift file dependencies
    :type thrift_dir_paths: list of str
    :param request_body: a JSON object representing the request body
    :type request_body: JSON
    :param return_json: whether or not to display the output in JSON format
    :type return_json: bool
    :param remove_generated_src: whether or not to delete the Python source generated from the Thrift files
    :type remove_generated_src: bool
    :param client_id: Finagle client id for identifying requests
    :type client_id: str
    :param proxy: [<proxy host>:<proxy port>] to route request through
    :type proxy: str
    :param verbose: log details
    :type verbose: bool

    """
    [service_name, method_name] = _split_endpoint(endpoint_name)
    environment_defined_paths = []
    if os.environ.get(THRIFT_PATH_ENVIRONMENT_VARIABLE):
        environment_defined_paths = os.environ[THRIFT_PATH_ENVIRONMENT_VARIABLE].split(':')
    cli = ThriftCLI(
        thrift_path,
        server_address,
        service_name,
        tls, tls_key_path, cert_verification_mode,
        thrift_dir_paths + environment_defined_paths,
        zookeeper,

        client_id=client_id,
        proxy=proxy
    )
    try:
        result = cli.run(method_name, request_body, return_json)
        if result is not None:
            print result
    finally:
        cli.cleanup(remove_generated_src)


def configure_logging(verbose):
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG if verbose else logging.INFO)


def _parse_args():
    """ Creates an ArgumentParser, parses sys.argv, and returns the desired arguments.

    :returns: a tuple of the desired arguments for _run_cli
    :rtype: tuple

    """
    parser = _make_parser()
    namespace = parser.parse_args()
    return namespace


def main():
    """ Runs a remote request and prints the result if it is not None. """
    args = _parse_args()
    configure_logging(args.verbose)
    _run_cli(*_parse_namespace(args))
