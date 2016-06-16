import shutil
import subprocess
import sys
import urlparse
import json

from .thrift_parser import ThriftParser

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class ThriftCLI(object):
    """ Provides an interface for setting up a client, making requests, and cleaning up.

    Call setup to open a connection with a server and inform ThriftCLI of the available endpoints.
    Call run to make a request.
    Call cleanup to close the connection and delete the generated python code.
    """
    def __init__(self):
        self._thrift_path = None
        self._server_address = None
        self._thrift_parser = ThriftParser()
        self._transport = None

    def setup(self, thrift_path, server_address):
        """ Opens a connection between the given thrift file and server.

        :param thrift_path: The path to the thrift file being used.
        :type thrift_path: str
        :param server_address: The address of the server to make requests to.
        :type server_address: str
        :returns: None
        """
        self._thrift_path = thrift_path
        self._server_address = server_address
        self._thrift_parser.parse(self._thrift_path)
        self._generate_and_import_module()
        self._open_connection(self._server_address)

    def run(self, endpoint, request_body):
        """ Runs the endpoint on the connected server as defined by the thrift file.

        :param endpoint: The name of the endpoint to ask the server to run.
        :type endpoint: str
        :param request_body: The arguments to provide as arguments to the endpoint.
        :type request_body: JSON or None
        :returns: endpoint result
        """
        method = self._get_method_from_endpoint(endpoint)
        [service_name, method_name] = self._split_endpoint(endpoint)
        request_args = self._convert_json_to_args(service_name, method_name, request_body)
        return method(**request_args)

    def cleanup(self):
        """ Deletes the gen-py code and closes the transport with the server.

        :returns: None
        """
        self._remove_dir('gen-py')
        if self._transport:
            self._transport.close()

    @staticmethod
    def _remove_dir(path):
        try:
            shutil.rmtree(path)
        except OSError:
            pass

    def _get_method_from_endpoint(self, endpoint):
        class_name = 'Client'
        [service_name, method_name] = self._split_endpoint(endpoint)
        client_constructor = getattr(self._get_service_module(service_name), class_name)
        client = client_constructor(self._protocol)
        try:
            method = getattr(client, method_name)
        except AttributeError:
            raise ThriftCLIException('\'%s\' service has no method \'%s\'' % (service_name, method_name))
        return method

    @staticmethod
    def _split_endpoint(endpoint):
        try:
            split = endpoint.split('.')
            if not split or len(split) != 2:
                raise ValueError()
            return split
        except ValueError:
            raise ThriftCLIException('Endpoint should be in format \'Service.method\'')

    def _get_service_module(self, service_name):
        service_reference = '.'.join([self._get_module_name(), service_name])
        try:
            return sys.modules[service_reference]
        except KeyError:
            raise ThriftCLIException('Invalid service \'%s\' provided' % service_name)

    def _generate_and_import_module(self):
        command = 'thrift -r --gen py %s' % self._thrift_path
        if subprocess.call(command, shell=True):
            raise ThriftCLIException('Thrift generation command failed.')
        sys.path.append('gen-py')
        self._import_module(self._get_module_name())

    @staticmethod
    def _import_module(module_name):
        module = __import__(module_name, globals())
        submodules = module.__all__
        for submodule in submodules:
            submodule_name = '.'.join([module_name, submodule])
            __import__(submodule_name, globals())

    def _get_module_name(self):
        return self._thrift_path[:-len('.thrift')].split('/')[-1]

    def _open_connection(self, address):
        (url, port) = self._parse_address_for_hostname_and_port(address)
        self._transport = TSocket.TSocket(url, port)
        self._transport = TTransport.TBufferedTransport(self._transport)
        self._protocol = TBinaryProtocol.TBinaryProtocol(self._transport)
        self._transport.open()

    @staticmethod
    def _parse_address_for_hostname_and_port(address):
        if '//' not in address:
            address = '//' + address
        url_obj = urlparse.urlparse(address)
        return url_obj.hostname, url_obj.port

    def _convert_json_to_args(self, service_name, method_name, data):

        fields = self._thrift_parser.get_fields_for_endpoint(service_name, method_name)
        return self._convert_json_to_args_given_fields(fields, data)

    def _convert_json_to_args_given_fields(self, fields, data):
        args = {field_name: self._convert_json_entry_to_arg(fields[field_name].field_type, value)
                for field_name, value in data.items()}
        return args

    def _convert_json_entry_to_arg(self, field_type, value):
        if self._thrift_parser.has_struct(field_type):
            fields = self._thrift_parser.get_fields_for_struct_name(field_type)
            value = self._convert_json_to_args_given_fields(fields, value)
        arg = self._construct_arg(field_type, value)
        return arg

    def _construct_arg(self, field_type, value):
        if self._thrift_parser.has_struct(field_type):
            return self._construct_struct_arg(field_type, value)
        elif self._thrift_parser.has_enum(field_type):
            return self._construct_enum_arg(field_type, value)
        elif field_type.startswith('list<'):
            return self._construct_list_arg(field_type, value)
        elif field_type.startswith('set<'):
            return self._construct_set_arg(field_type, value)
        elif field_type.startswith('map<'):
            return self._construct_map_arg(field_type, value)
        return value

    def _construct_struct_arg(self, field_type, value):
        return getattr(self._get_service_module('ttypes'), field_type)(**value)

    def _construct_enum_arg(self, field_type, value):
        enum_class = getattr(self._get_service_module('ttypes'), field_type)
        if isinstance(value, (int, long)):
            return value
        elif isinstance(value, basestring):
            return enum_class._NAMES_TO_VALUES[value]
        raise ThriftCLIException('Invalid value provided for enum %s: %s' % (field_type.str(value)))

    def _construct_list_arg(self, field_type, value):
        elem_type = field_type[field_type.index('<') + 1:field_type.rindex('>')]
        return tuple([self._convert_json_entry_to_arg(elem_type, elem) for elem in value])

    def _construct_set_arg(self, field_type, value):
        elem_type = field_type[field_type.index('<') + 1:field_type.rindex('>')]
        return frozenset([self._convert_json_entry_to_arg(elem_type, elem) for elem in value])

    def _construct_map_arg(self, field_type, value):
        types_string = field_type[field_type.index('<') + 1:field_type.rindex('>')]
        split_index = self._calc_map_types_split_index(types_string)
        if split_index == -1:
            raise ThriftCLIException('Invalid type formatting for map - \'%s\'' % types_string)
        key_type = types_string[:split_index].strip()
        elem_type = types_string[split_index + 1:].strip()
        prep = lambda x: json.loads(x) if self._thrift_parser.has_struct(key_type) else x
        return {self._convert_json_entry_to_arg(key_type, prep(key)): self._convert_json_entry_to_arg(elem_type, elem)
                for key, elem in value.items()}

    @staticmethod
    def _calc_map_types_split_index(types_string):
        bracket_depth = 0
        for i, char in enumerate(types_string):
            if char == '<':
                bracket_depth += 1
            elif char == '>':
                bracket_depth -= 1
            elif char == ',' and bracket_depth == 0:
                return i
        return -1


class ThriftCLIException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
