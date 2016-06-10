import shutil
import subprocess
import sys
import urlparse

from .thrift_parser import ThriftParser

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol


class ThriftCLI(object):
    def __init__(self):
        self._thrift_path = None
        self._server_address = None
        self._thrift_parser = ThriftParser()
        self._transport = None

    def setup(self, thrift_path, server_address):
        """ Opens a connection between the given thrift file and server. """
        self._thrift_path = thrift_path
        self._server_address = server_address
        self._thrift_parser.parse(self._thrift_path)
        self._generate_and_import_module()
        self._open_connection()

    def run(self, endpoint, request_body):
        """ Runs the endpoint on the connected server as defined by the thrift file.
        The request_body is transformed into the endpoint's arguments. """
        method = self._get_method_from_endpoint(endpoint)
        [service_name, method_name] = self._split_endpoint(endpoint)
        request_args = self.convert_json_to_args(service_name, method_name, request_body)
        print request_args
        return method(**request_args)

    def cleanup(self):
        """ Deletes the gen-py code and closes the transport with the server. """
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
        subprocess.call(command, shell=True)
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

    def _open_connection(self):
        (url, port) = self._parse_address_for_hostname_and_port()
        self._transport = TSocket.TSocket(url, port)
        self._transport = TTransport.TBufferedTransport(self._transport)
        self._protocol = TBinaryProtocol.TBinaryProtocol(self._transport)
        self._transport.open()

    def _parse_address_for_hostname_and_port(self):
        address_to_parse = self._server_address
        if '//' not in address_to_parse:
            address_to_parse = '//' + address_to_parse
        url_obj = urlparse.urlparse(address_to_parse)
        return url_obj.hostname, url_obj.port

    def convert_json_to_args(self, service_name, method_name, data):
        fields = self._thrift_parser.get_fields_for_endpoint(service_name, method_name)
        return self._convert_json_to_args_given_fields(fields, data)

    def _convert_json_to_args_given_fields(self, fields, data):
        args = {field_name: self._convert_json_entry_to_arg(fields[field_name], value)
                for field_name, value in data.items()}
        return args

    def _convert_json_entry_to_arg(self, field, value):
        if isinstance(value, dict):
            fields = self._thrift_parser.get_fields_for_struct_name(field.field_type)
            value = self._convert_json_to_args_given_fields(fields, value)
        arg = self._construct_arg(field, value)
        return arg

    def _construct_arg(self, field, value):
        if self._thrift_parser.has_struct(field.field_type):
            return self._construct_struct_arg(field, value)
        elif self._thrift_parser.has_enum(field.field_type):
            return self._construct_enum_arg(field, value)
        return value

    def _construct_struct_arg(self, field, value):
        return getattr(self._get_service_module('ttypes'), field.field_type)(**value)

    def _construct_enum_arg(self, field, value):
        enum_class = getattr(self._get_service_module('ttypes'), field.field_type)
        if isinstance(value, (int, long)):
            return value
        elif isinstance(value, basestring):
            return enum_class._NAMES_TO_VALUES[value]
        raise TypeError('Invalid value provided for enum %s: %s' % (field.field_type. str(value)))



class ThriftCLIException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
