import argparse
import json
import os

from thrift_zookeeper_resolver import get_server_address
from .thrift_argument_converter import ThriftArgumentConverter
from .thrift_cli_error import ThriftCLIError
from .thrift_executor import ThriftExecutor
from .thrift_parser import ThriftParser
from .request_body_converter import convert


class ThriftCLI(object):
    """ Provides an interface for setting up a client, making requests, and cleaning up.

    Call init to open a connection with a server and inform ThriftCLI of the available endpoints.
    Call run to make a request.
    Call cleanup to close the connection and delete the generated python code.
    """

    def __init__(self, thrift_path, server_address, service_name, thrift_dir_paths=None, zookeeper=False):
        """
        :param thrift_path: The path to the thrift file being used.
        :type thrift_path: str
        :param server_address: The address of the server to make requests to.
        :type server_address: str
        :param thrift_dir_paths: Additional directories to search for included thrift files in.
        :type thrift_dir_paths: list of str
        :param zookeeper: Whether or not to treat the server address as a zookeeper host with a path.
        :type zookeeper: bool

        """
        self._thrift_path = thrift_path
        self._thrift_argument_converter = ThriftArgumentConverter(thrift_path, thrift_dir_paths)
        self._service_reference = '%s.%s' % (ThriftParser.get_package_name(self._thrift_path), service_name)
        if zookeeper:
            server_address = get_server_address(server_address, service_name)
        self._thrift_executor = ThriftExecutor(
            thrift_path, server_address, self._service_reference, thrift_dir_paths)

    def run(self, method_name, request_body, return_json=False):
        """ Runs the endpoint on the connected server as defined by the thrift file.

        :param method_name: The name of the method to ask the server to run.
        :type method_name: str
        :param request_body: The arguments to provide as arguments to the endpoint.
        :type request_body: dict
        :param return_json: Returns result in JSON format if True, python object if False.
        :type return_json: bool
        :returns: endpoint result

        """
        request_args = self._thrift_argument_converter.convert_args(self._service_reference, method_name, request_body)
        result = self._thrift_executor.run(method_name, request_args)
        if return_json:
            result = json.dumps(result, default=lambda o: o.__dict__)
        return result

    def cleanup(self, remove_generated_src=False):
        """ Deletes the gen-py code and closes the transport with the server. """
        self._thrift_executor.cleanup(remove_generated_src)


def _split_endpoint(endpoint):
    """ Extracts the service name and method name from an endpoint. """
    split = endpoint.split('.')
    if not split or len(split) != 2:
        raise ThriftCLIError('Endpoint should be in format \'Service.function\', given: \'%s\'' % endpoint)
    return split


def _load_file(path):
    """ Returns the contents of a file. """
    with open(path, 'r') as file_to_read:
        return file_to_read.read()


def _load_request_body(request_body_arg):
    """ Parses the request body argument into an argument dictionary. """
    if not request_body_arg:
        return {}
    if os.path.isfile(request_body_arg):
        request_body_arg = _load_file(request_body_arg)
    try:
        return convert(request_body_arg)
    except ValueError, e:
        raise ThriftCLIError(e)


def _parse_namespace(args):
    """ Converts the namespace object returned by argparse into the desired variables. """
    server_address = args.server_address
    endpoint = args.endpoint
    thrift_path = args.thrift_path
    thrift_dir_paths = args.include
    request_body = _load_request_body(args.body)
    zookeeper = args.zookeeper
    return_json = args.json
    cleanup = args.cleanup
    return server_address, endpoint, thrift_path, thrift_dir_paths, request_body, zookeeper, return_json, cleanup


def _make_parser():
    """ Initializes the ArgumentParser with all desired arguments. """
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
    parser.add_argument('-c', '--cleanup', action='store_true',
                        help='remove generated code after execution')
    parser.add_argument('-j', '--json', action='store_true',
                        help='print result in JSON format')
    return parser


def _run_cli(server_address, endpoint_name, thrift_path, thrift_dir_paths, request_body, zookeeper, return_json,
             remove_generated_src):
    """ Runs a remote request and prints the result if it is not None. """
    [service_name, method_name] = _split_endpoint(endpoint_name)
    cli = ThriftCLI(thrift_path, server_address, service_name, thrift_dir_paths, zookeeper)
    try:
        result = cli.run(method_name, request_body, return_json)
        if result is not None:
            print result
    finally:
        cli.cleanup(remove_generated_src)


def _parse_args():
    """ Creates an ArgumentParser, parses sys.argv, and returns the desired arguments. """
    parser = _make_parser()
    namespace = parser.parse_args()
    return _parse_namespace(namespace)


def main():
    """ Runs a remote request and prints the result if it is not None. """
    args = _parse_args()
    _run_cli(*args)
