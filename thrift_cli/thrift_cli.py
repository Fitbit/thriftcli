import sys
import subprocess
import imp
import urlparse
import shutil

from .thrift_parser import ThriftParser
from .thrift_service import ThriftService
from .thrift_struct import ThriftStruct

# import inspect
# from argparse import Namespace

from thrift import Thrift
from thrift.Thrift import TType
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

class ThriftCLI(object):

	def setup(self, thrift_path, server_address):
		""" Opens a connection between the given thrift file and server. """
		self._thrift_path = thrift_path
		self._server_address = server_address
		self._parse_thrift()
		self._generate_and_import_code()
		self._open_connection()

	def run(self, endpoint, request_body):
		""" Runs the endpoint on the connected server as defined by the thrift file.
		The request_body is transformed into the endpoint's arguments. """
		method = self._get_method_from_endpoint(endpoint)
		request_args = self._json_to_object(request_body)
		return method(**request_args)

	def cleanup(self):
		""" Deletes the gen-py code and closes the transport with the server. """
		shutil.rmtree('gen-py')
		self._transport.close()

	def _parse_thrift(self):
		tparser = ThriftParser()
		tparse_result = tparser.parse(self._thrift_path)
		return tparse_result

	def _get_method_from_endpoint(self, endpoint):
		class_name = 'Client'
		[service_name, method_name] = endpoint.split('.')
		service_reference = '.'.join([self._get_module_name(), service_name])
		client_constructor_attr_name = '.'.join([service_reference, class_name])
		# print mod
		members = [member for member in inspect.getmembers(mod)]
		# for member in members:
		# 	print member
		client_constructor = getattr(self._get_module(), client_constructor_attr_name)
		# print client_constructor
		client = client_constructor(self._protocol)
		# print client
		method = getattr(client, method_name)
		return method

	def _json_to_object(self, data):
		# return json.loads(data, object_hook=lambda d: Namespace(**d))
		return {}

	def _generate_and_import_code(self):
		command = 'thrift -r --gen py %s' % self._thrift_path
		subprocess.call(command, shell=True)
		imp.load_source(self._get_module_name(), self._get_module_path())

	def _get_module_name(self):
		return self._thrift_path[:-len('.thrift')].split('/')[-1]

	def _get_module_path(self):
		return 'gen-py/%s' % self._get_module_name()

	def _get_module(self):
		return sys.modules[self._get_module_name()]

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
		return (url_obj.hostname, url_obj.port)

class ThriftCLIException(Exception):

	def __init__(self,*args,**kwargs):
		Exception.__init__(self,*args,**kwargs)