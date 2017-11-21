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
from thriftcli import ThriftParser, ThriftParseResult, ThriftCLIError


class TestThriftParser(unittest.TestCase):
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        expected_parse_result = data.TEST_THRIFT_PARSE_RESULT
        parse_result = parser.parse()
        self.assertEqual(parse_result, expected_parse_result)

    @mock.patch('os.path.isfile')
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_including(self, mock_load_file, mock_is_file):
        mock_load_file.side_effect = [data.TEST_THRIFT_INCLUDING_CONTENT, data.TEST_THRIFT_INCLUDED_CONTENT]
        mock_is_file.side_effect = lambda path: path == data.TEST_THRIFT_INCLUDED_PATH
        parser = ThriftParser(data.TEST_THRIFT_INCLUDING_PATH, [data.TEST_THRIFT_DIR_PATH])
        expected_parse_result = data.TEST_THRIFT_INCLUDING_PARSE_RESULT
        parse_result = parser.parse()
        expected_call_args_list = [mock.call(data.TEST_THRIFT_INCLUDING_PATH),
                                   mock.call(data.TEST_THRIFT_INCLUDED_PATH)]
        self.assertEqual(mock_load_file.call_args_list, expected_call_args_list)
        self.assertEqual(parse_result, expected_parse_result)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_structs(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser._references = data.TEST_THRIFT_REFERENCES
        expected_structs = data.TEST_THRIFT_STRUCTS
        structs = parser._parse_structs()
        self.assertDictEqual(structs, expected_structs)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_services(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser._references = data.TEST_THRIFT_REFERENCES
        parser._result = ThriftParseResult()
        expected_services = data.TEST_THRIFT_SERVICES
        services = parser._parse_services()
        self.assertDictEqual(services, expected_services)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_enums(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser._references = data.TEST_THRIFT_REFERENCES
        expected_enums = data.TEST_THRIFT_ENUMS
        enums = parser._parse_enums()
        self.assertEqual(enums, expected_enums)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_typedefs(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser._references = data.TEST_THRIFT_REFERENCES
        expected_typedefs = data.TEST_THRIFT_TYPEDEFS
        typedefs = parser._parse_typedefs()
        self.assertEqual(typedefs, expected_typedefs)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_references(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        expected_references = data.TEST_THRIFT_REFERENCES
        references = parser._parse_references()
        self.assertEqual(references, expected_references)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_endpoints_from_service_definition(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser._references = data.TEST_THRIFT_REFERENCES
        endpoints = parser._parse_endpoints_from_service_definition(data.TEST_THRIFT_SERVICE_DEFINITION)
        expected_endpoints = data.TEST_THRIFT_SERVICE_ENDPOINTS
        self.assertEqual(endpoints, expected_endpoints)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_struct_definitions(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser._references = data.TEST_THRIFT_REFERENCES
        expected_struct_definitions = {
            data.TEST_THRIFT_STRUCT_REFERENCE: data.TEST_THRIFT_STRUCT_DEFINITION,
            data.TEST_THRIFT_STRUCT_REFERENCE2: data.TEST_THRIFT_STRUCT_DEFINITION2,
            data.TEST_THRIFT_STRUCT_REFERENCE3: data.TEST_THRIFT_STRUCT_DEFINITION3
        }
        struct_definitions = parser._parse_struct_definitions()
        self.assertEqual(struct_definitions, expected_struct_definitions)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_service_definitions(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser._references = data.TEST_THRIFT_REFERENCES
        expected_service_definitions = [
            (data.TEST_THRIFT_SERVICE_REFERENCE, (data.TEST_THRIFT_SERVICE_DEFINITION, None)),
            (data.TEST_THRIFT_SERVICE_REFERENCE2, (data.TEST_THRIFT_SERVICE_DEFINITION2, None)),
            (data.TEST_THRIFT_SERVICE_REFERENCE3, (data.TEST_THRIFT_SERVICE_DEFINITION3,
                                                   data.TEST_THRIFT_SERVICE_REFERENCE))
        ]
        service_definitions = parser._parse_service_definitions()
        self.assertEqual(service_definitions, expected_service_definitions)

    def test_split_fields_string(self):
        fields_string = '1:i32 num1, 2:i32 num2, 3:Operation op'
        expected_field_strings = ['1:i32 num1', '2:i32 num2', '3:Operation op']
        field_strings = ThriftParser.split_fields_string(fields_string)
        self.assertEqual(field_strings, expected_field_strings)
        fields_string = '1:map<string, string> stringMap, 2:set<list<SomeStruct>> setOfLists'
        expected_field_strings = ['1:map<string, string> stringMap', '2:set<list<SomeStruct>> setOfLists']
        field_strings = ThriftParser.split_fields_string(fields_string)
        self.assertEqual(field_strings, expected_field_strings)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_unalias_type(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parse_result = parser.parse()
        expected_unaliased = data.TEST_THRIFT_UNALIASED_TYPES
        unaliased = {alias: parse_result.unalias_type(alias) for alias in data.TEST_THRIFT_UNALIASED_TYPES}
        self.assertDictEqual(unaliased, expected_unaliased)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_unalias_type_circular(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT_CIRCULAR_TYPEDEFS
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parse_result = parser.parse()
        for alias in data.TEST_THRIFT_CIRCULAR_TYPEDEFS:
            with self.assertRaises(ThriftCLIError):
                parse_result.unalias_type(alias)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_apply_namespace_on_references(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser.parse()
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_ENUM_NAME), data.TEST_THRIFT_ENUM_REFERENCE)
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_ENUM_NAME2), data.TEST_THRIFT_ENUM_REFERENCE2)
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_STRUCT_NAME), data.TEST_THRIFT_STRUCT_REFERENCE)
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_STRUCT_NAME2), data.TEST_THRIFT_STRUCT_REFERENCE2)
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_STRUCT_NAME3), data.TEST_THRIFT_STRUCT_REFERENCE3)
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_SERVICE_NAME), data.TEST_THRIFT_SERVICE_REFERENCE)
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_SERVICE_NAME2), data.TEST_THRIFT_SERVICE_REFERENCE2)
        self.assertEqual(parser._apply_namespace(data.TEST_THRIFT_SERVICE_NAME3), data.TEST_THRIFT_SERVICE_REFERENCE3)
        self.assertEqual(
            parser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME),
            data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE)
        self.assertEqual(
            parser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME2),
            data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2)
        self.assertEqual(
            parser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME3),
            data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE3)
        self.assertEqual(
            parser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME4),
            data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE4)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_apply_namespace_on_primitives(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser.parse()
        self.assertEqual(parser._apply_namespace('i32'), 'i32')
        self.assertEqual(parser._apply_namespace('bool'), 'bool')
        self.assertEqual(parser._apply_namespace('string'), 'string')
        self.assertEqual(parser._apply_namespace('binary'), 'binary')

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_apply_namespace_on_data_structures(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        parser = ThriftParser(data.TEST_THRIFT_PATH)
        parser.parse()
        self.assertEqual(parser._apply_namespace('set<bool>'), 'set<bool>')
        self.assertEqual(
            parser._apply_namespace('map<string, map<string, list<set<binary>>>>'),
            'map<string, map<string, list<set<binary>>>>')
        self.assertEqual(
            parser._apply_namespace('list<set<%s>>' % data.TEST_THRIFT_TYPEDEF_ALIAS_NAME),
            'list<set<%s>>' % data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE)
        self.assertEqual(
            parser._apply_namespace('map<%s, list<%s>>' % (data.TEST_THRIFT_STRUCT_NAME, data.TEST_THRIFT_ENUM_NAME)),
            'map<%s, list<%s>>' % (data.TEST_THRIFT_STRUCT_REFERENCE, data.TEST_THRIFT_ENUM_REFERENCE))

    def test_calc_map_types_split_index(self):
        test_map_type = 'string, string'
        test_map_type2 = 'map<string, list<i32>>, set<string>'
        expected_split_index = len('string')
        expected_split_index2 = len('map<string, list<i32>>')
        split_index = ThriftParser.calc_map_types_split_index(test_map_type)
        split_index2 = ThriftParser.calc_map_types_split_index(test_map_type2)
        self.assertEqual(split_index, expected_split_index)
        self.assertEqual(split_index2, expected_split_index2)

    def test_get_package_name(self):
        expected_module_name = data.TEST_THRIFT_MODULE_NAME
        module_name = ThriftParser.get_package_name(data.TEST_THRIFT_PATH)
        self.assertEqual(module_name, expected_module_name)
