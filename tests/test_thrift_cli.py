import unittest

import mock

from thrift_cli import ThriftCLI
import data


class TestThriftCLI(unittest.TestCase):
    @mock.patch('thrift_cli.TSocket.TSocket')
    @mock.patch('thrift_cli.ThriftCLI._import_module')
    @mock.patch('subprocess.call')
    @mock.patch('thrift_cli.ThriftParser._load_file')
    def test_setup(self, mock_load_file, mock_call, mock_import_module, mock_tsocket):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        mock_call.side_effect = None
        cli = ThriftCLI()
        cli.setup(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS)
        command = 'thrift -r --gen py %s' % data.TEST_THRIFT_PATH
        mock_call.assert_called_with(command, shell=True)
        mock_import_module.assert_called_with(data.TEST_THRIFT_MODULE_NAME)
        mock_tsocket.assert_called_with(data.TEST_SERVER_URL, data.TEST_PORT)

    @mock.patch('thrift_cli.TSocket.TSocket')
    @mock.patch('thrift_cli.ThriftCLI._import_module')
    @mock.patch('subprocess.call')
    @mock.patch('thrift_cli.ThriftParser._load_file')
    @mock.patch('thrift_cli.ThriftCLI._remove_dir')
    def test_cleanup(self, mock_remove_dir, mock_load_file, mock_call, mock_import_module, mock_tsocket):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        mock_import_module.side_effect = None
        mock_call.side_effect = None
        mock_remove_dir.side_effect = None
        cli = ThriftCLI()
        cli.setup(data.TEST_THRIFT_PATH, data.TEST_SERVER_ADDRESS)
        cli.cleanup()
        expected_rm_path = 'gen-py'
        command = 'thrift -r --gen py %s' % data.TEST_THRIFT_PATH
        mock_call.assert_called_with(command, shell=True)
        self.assertTrue(mock_remove_dir.called)
        mock_remove_dir.assert_called_with(expected_rm_path)

    def test_get_module_name(self):
        cli = ThriftCLI()
        cli._thrift_path = data.TEST_THRIFT_PATH
        expected_module_name = data.TEST_THRIFT_MODULE_NAME
        module_name = cli._get_module_name()
        self.assertEqual(module_name, expected_module_name)