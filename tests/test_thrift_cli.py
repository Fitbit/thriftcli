import mock
import unittest
from . import data
from thrift_cli import ThriftCLI
from thrift.Thrift import TType

class TestThriftCLI(unittest.TestCase):

	@mock.patch('thrift_cli.TSocket.TSocket')
	@mock.patch('imp.load_source')
	@mock.patch('subprocess.call')
	@mock.patch('thrift_cli.ThriftParser._load_file')
	def test_setup(self, mock_load_file, mock_call, mock_load_source, mock_tsocket):
		mock_load_file.return_value = data.TEST_THRIFT_CONTENT
		mock_call.side_effect = None
		cli = ThriftCLI()
		cli.setup(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS)
		command = 'thrift -r --gen py %s' % data.TEST_THRIFT_PATH
		mock_call.assert_called_with(command, shell=True)
		mock_load_source.assert_called_with(data.TEST_THRIFT_MODULE_NAME, data.TEST_THRIFT_MODULE_PATH)
		mock_tsocket.assert_called_with(data.TEST_SERVER_URL, data.TEST_PORT)

	@mock.patch('shutil.rmtree')
	@mock.patch('thrift_cli.TSocket.TSocket')
	@mock.patch('imp.load_source')
	@mock.patch('subprocess.call')
	@mock.patch('thrift_cli.ThriftParser._load_file')
	def test_cleanup(self, mock_load_file, mock_call, mock_load_source, mock_tsocket, mock_rmtree):
		mock_load_file.return_value = data.TEST_THRIFT_CONTENT
		mock_call.side_effect = None
		mock_rmtree.side_effect = None
		cli = ThriftCLI()
		cli.setup(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS)
		cli.cleanup()
		expected_rm_path = 'gen-py'
		mock_rmtree.assert_called_with(expected_rm_path)

	def test_get_module_name(self):
		cli = ThriftCLI()
		cli._thrift_path = data.TEST_THRIFT_PATH
		expected_module_name = data.TEST_THRIFT_MODULE_NAME
		module_name = cli._get_module_name()
		self.assertEqual(module_name, expected_module_name)

	def test_get_module_path(self):
		cli = ThriftCLI()
		cli._thrift_path = data.TEST_THRIFT_PATH
		expected_module_path = data.TEST_THRIFT_MODULE_PATH
		module_path = cli._get_module_path()
		self.assertEqual(module_path, expected_module_path)

	# def test_parse_address_for_hostname_and_port(self):
	# 	self.fail()