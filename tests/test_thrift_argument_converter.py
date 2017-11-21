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

import unittest

import mock

from tests import data
from thriftcli import ThriftArgumentConverter, ThriftCLIError


class TestThriftArgumentConverter(unittest.TestCase):
    def test_split_field_type(self):
        field_type = data.TEST_THRIFT_STRUCT_REFERENCE
        expected_namespace, expected_struct_name = data.TEST_THRIFT_NAMESPACE, data.TEST_THRIFT_STRUCT_NAME
        namespace, struct_name = ThriftArgumentConverter._split_field_type(field_type)
        self.assertEqual((namespace, struct_name), (expected_namespace, expected_struct_name))
        field_type = '%s%s' % (data.TEST_THRIFT_NAMESPACE, data.TEST_THRIFT_STRUCT_NAME)
        with self.assertRaises(ThriftCLIError):
            ThriftArgumentConverter._split_field_type(field_type)
        field_type = '%s.%s.abc' % (data.TEST_THRIFT_NAMESPACE, data.TEST_THRIFT_STRUCT_NAME)
        with self.assertRaises(ThriftCLIError):
            ThriftArgumentConverter._split_field_type(field_type)

    @mock.patch('thriftcli.ThriftArgumentConverter._get_type_class')
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_convert_args_with_multiple_args(self, mock_load_file, mock_get_type_class):
        op_mock = mock.Mock(_NAMES_TO_VALUES={'A': 0})
        mock_get_type_class.return_value = op_mock
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        converter = ThriftArgumentConverter(data.TEST_THRIFT_PATH)
        args = converter.convert_args(data.TEST_THRIFT_SERVICE_REFERENCE, 'doSomething1', data.TEST_JSON_TO_CONVERT)
        expected_args = {
            "num1": 3,
            "num2": 4,
            "op": 0
        }
        expected_call_args_list = [mock.call('Something', 'SomeEnum')]
        self.assertEqual(mock_get_type_class.call_args_list, expected_call_args_list)
        self.assertEqual(args, expected_args)

    @mock.patch('thriftcli.ThriftArgumentConverter._get_type_class')
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_convert_args_with_inference(self, mock_load_file, mock_get_type_class):
        struct_obj_mock = mock.Mock()
        struct_mock = mock.Mock(return_value=struct_obj_mock)
        mock_get_type_class.return_value = struct_mock
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        converter = ThriftArgumentConverter(data.TEST_THRIFT_PATH)
        struct_args = {"thing_one": "some string", "thing_two": 2.0, "thing_three": True}
        args = converter.convert_args(
            data.TEST_THRIFT_SERVICE_REFERENCE,
            'useSomeStruct',
            struct_args)
        expected_args = {
            "someStruct": struct_obj_mock
        }
        struct_mock.assert_called_with(**struct_args)
        self.assertEqual(args, expected_args)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_convert_args_with_map_typedef(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        converter = ThriftArgumentConverter(data.TEST_THRIFT_PATH)
        args = converter.convert_args(data.TEST_THRIFT_SERVICE_REFERENCE3, 'passMap', data.TEST_JSON_TO_CONVERT2)
        expected_args = data.TEST_JSON_TO_CONVERT2
        self.assertEqual(args, expected_args)

    @mock.patch('thriftcli.ThriftArgumentConverter._get_type_class')
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_convert_args_with_nested_structure_of_structs(self, mock_load_file, mock_get_type_class):
        mock_struct_constructor = mock.Mock()
        mock_struct_constructor.side_effect = [0, 1, 2]
        mock_get_type_class.return_value = mock_struct_constructor
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        converter = ThriftArgumentConverter(data.TEST_THRIFT_PATH)
        args = converter.convert_args(data.TEST_THRIFT_SERVICE_REFERENCE3, 'passSetOfLists', data.TEST_JSON_TO_CONVERT3)
        expected_args = {
            "setOfLists": frozenset([
                tuple([0, 1]),
                tuple([2])
            ])
        }
        self.assertEqual(args, expected_args)
        expected_call_args_list = [mock.call(data.TEST_THRIFT_NAMESPACE, data.TEST_THRIFT_STRUCT_NAME)] * 3
        self.assertEqual(mock_get_type_class.call_args_list, expected_call_args_list)
        expected_call_args = sum([item for sublist in data.TEST_JSON_TO_CONVERT3.values() for item in sublist], [])
        expected_call_args_list = [mock.call(**call_args) for call_args in expected_call_args]
        self.assertEqual(mock_struct_constructor.call_args_list, expected_call_args_list)
