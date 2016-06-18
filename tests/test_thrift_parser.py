import unittest
import mock
import data
from thriftcli import ThriftParser, ThriftCLIException


class TestThriftParser(unittest.TestCase):
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        tparser = ThriftParser()
        expected_tparse_result = data.TEST_THRIFT_PARSE_RESULT
        tparse_result = tparser.parse(data.TEST_THRIFT_PATH)
        self.assertEqual(tparse_result, expected_tparse_result)

    @mock.patch('os.path.isfile')
    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_parse_including(self, mock_load_file, mock_is_file):
        mock_load_file.side_effect = [data.TEST_THRIFT_INCLUDING_CONTENT, data.TEST_THRIFT_INCLUDED_CONTENT]
        mock_is_file.side_effect = lambda path: path == data.TEST_THRIFT_INCLUDED_PATH
        tparser = ThriftParser()
        expected_tparse_result = data.TEST_THRIFT_INCLUDING_PARSE_RESULT
        tparse_result = tparser.parse(data.TEST_THRIFT_INCLUDING_PATH, [data.TEST_THRIFT_DIR_PATH])
        expected_call_args_list = [mock.call(data.TEST_THRIFT_INCLUDING_PATH),
                                   mock.call(data.TEST_THRIFT_INCLUDED_PATH)]
        self.assertEqual(mock_load_file.call_args_list, expected_call_args_list)
        self.assertEqual(tparse_result, expected_tparse_result)

    def test_parse_structs(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        tparser._defined_references = data.TEST_THRIFT_DEFINED_REFERENCES
        expected_structs = data.TEST_THRIFT_STRUCTS
        structs = tparser._parse_structs()
        self.assertDictEqual(structs, expected_structs)

    def test_parse_services(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        tparser._defined_references = data.TEST_THRIFT_DEFINED_REFERENCES
        tparser.result = ThriftParser.Result(
            data.TEST_THRIFT_STRUCTS, {}, data.TEST_THRIFT_ENUMS, data.TEST_THRIFT_TYPEDEFS)
        expected_services = data.TEST_THRIFT_SERVICES
        services = tparser._parse_services()
        self.assertDictEqual(services, expected_services)

    def test_parse_enums(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        tparser._defined_references = data.TEST_THRIFT_DEFINED_REFERENCES
        expected_enums = data.TEST_THRIFT_ENUMS
        enums = tparser._parse_enums()
        self.assertEqual(enums, expected_enums)

    def test_parse_typedefs(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        tparser._defined_references = data.TEST_THRIFT_DEFINED_REFERENCES
        tparser.result = ThriftParser.Result(data.TEST_THRIFT_STRUCTS, {}, set([]), {})
        expected_typedefs = data.TEST_THRIFT_TYPEDEFS
        typedefs = tparser._parse_typedefs()
        self.assertEqual(typedefs, expected_typedefs)

    def test_get_defined_references(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        tparser._dependency_parsers = []
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        expected_defined_references = data.TEST_THRIFT_DEFINED_REFERENCES
        defined_references = tparser.get_defined_references()
        self.assertEqual(defined_references, expected_defined_references)

    def test_parse_endpoints_from_service_definition(self):
        tparser = ThriftParser()
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        tparser._defined_references = data.TEST_THRIFT_DEFINED_REFERENCES
        endpoints = tparser._parse_endpoints_from_service_definition(data.TEST_THRIFT_SERVICE_DEFINITION)
        expected_endpoints = data.TEST_THRIFT_SERVICE_ENDPOINTS
        self.assertEqual(endpoints, expected_endpoints)

    def test_parse_struct_definitions(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        expected_struct_definitions = {
            data.TEST_THRIFT_STRUCT_REFERENCE: data.TEST_THRIFT_STRUCT_DEFINITION,
            data.TEST_THRIFT_STRUCT_REFERENCE2: data.TEST_THRIFT_STRUCT_DEFINITION2,
            data.TEST_THRIFT_STRUCT_REFERENCE3: data.TEST_THRIFT_STRUCT_DEFINITION3
        }
        struct_definitions = tparser._parse_struct_definitions()
        self.assertEqual(struct_definitions, expected_struct_definitions)

    def test_parse_service_definitions(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        tparser._namespace = data.TEST_THRIFT_NAMESPACE
        expected_service_definitions = {
            data.TEST_THRIFT_SERVICE_REFERENCE: data.TEST_THRIFT_SERVICE_DEFINITION,
            data.TEST_THRIFT_SERVICE_REFERENCE2: data.TEST_THRIFT_SERVICE_DEFINITION2,
            data.TEST_THRIFT_SERVICE_REFERENCE3: data.TEST_THRIFT_SERVICE_DEFINITION3
        }
        service_definitions = tparser._parse_service_definitions()
        self.assertEqual(service_definitions, expected_service_definitions)

    def test_split_fields_string(self):
        tparser = ThriftParser()
        fields_string = '1:i32 num1, 2:i32 num2, 3:Operation op'
        expected_field_strings = ['1:i32 num1', '2:i32 num2', '3:Operation op']
        field_strings = tparser._split_fields_string(fields_string)
        self.assertEqual(field_strings, expected_field_strings)
        fields_string = '1:map<string, string> stringMap, 2:set<list<SomeStruct>> setOfLists'
        expected_field_strings = ['1:map<string, string> stringMap', '2:set<list<SomeStruct>> setOfLists']
        field_strings = tparser._split_fields_string(fields_string)
        self.assertEqual(field_strings, expected_field_strings)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_unalias_type(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        tparser = ThriftParser()
        tparser.parse(data.TEST_THRIFT_PATH)
        expected_unaliased = data.TEST_THRIFT_UNALIASED_TYPES
        unaliased = {alias: tparser.unalias_type(alias) for alias in data.TEST_THRIFT_UNALIASED_TYPES}
        self.assertDictEqual(unaliased, expected_unaliased)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_unalias_type_circular(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT_CIRCULAR_TYPEDEFS
        tparser = ThriftParser()
        tparser.parse(data.TEST_THRIFT_PATH)
        for alias in data.TEST_THRIFT_CIRCULAR_TYPEDEFS:
            with self.assertRaises(ThriftCLIException):
                tparser.unalias_type(alias)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_apply_namespace_on_defined_references(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        tparser = ThriftParser()
        tparser.parse(data.TEST_THRIFT_PATH)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_ENUM_NAME), data.TEST_THRIFT_ENUM_REFERENCE)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_ENUM_NAME2), data.TEST_THRIFT_ENUM_REFERENCE2)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_STRUCT_NAME), data.TEST_THRIFT_STRUCT_REFERENCE)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_STRUCT_NAME2), data.TEST_THRIFT_STRUCT_REFERENCE2)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_STRUCT_NAME3), data.TEST_THRIFT_STRUCT_REFERENCE3)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_SERVICE_NAME), data.TEST_THRIFT_SERVICE_REFERENCE)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_SERVICE_NAME2), data.TEST_THRIFT_SERVICE_REFERENCE2)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_SERVICE_NAME3), data.TEST_THRIFT_SERVICE_REFERENCE3)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME),
                         data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME2),
                         data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME3),
                         data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE3)
        self.assertEqual(tparser._apply_namespace(data.TEST_THRIFT_TYPEDEF_ALIAS_NAME4),
                         data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE4)

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_apply_namespace_on_primitives(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        tparser = ThriftParser()
        tparser.parse(data.TEST_THRIFT_PATH)
        self.assertEqual(tparser._apply_namespace('i32'), 'i32')
        self.assertEqual(tparser._apply_namespace('bool'), 'bool')
        self.assertEqual(tparser._apply_namespace('string'), 'string')
        self.assertEqual(tparser._apply_namespace('binary'), 'binary')

    @mock.patch('thriftcli.ThriftParser._load_file')
    def test_apply_namespace_on_data_structures(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        tparser = ThriftParser()
        tparser.parse(data.TEST_THRIFT_PATH)
        self.assertEqual(tparser._apply_namespace('set<bool>'), 'set<bool>')
        self.assertEqual(tparser._apply_namespace('map<string, map<string, list<set<binary>>>>'),
                         'map<string, map<string, list<set<binary>>>>')
        self.assertEqual(tparser._apply_namespace('list<set<%s>>' % data.TEST_THRIFT_TYPEDEF_ALIAS_NAME),
                         'list<set<%s>>' % data.TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE)
        self.assertEqual(tparser._apply_namespace('map<%s, list<%s>>' %
                                                  (data.TEST_THRIFT_STRUCT_NAME, data.TEST_THRIFT_ENUM_NAME)),
                         'map<%s, list<%s>>' % (data.TEST_THRIFT_STRUCT_REFERENCE, data.TEST_THRIFT_ENUM_REFERENCE))
