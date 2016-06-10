import unittest

import mock

import data
from thrift_cli import ThriftParser


class TestThriftParser(unittest.TestCase):
    @mock.patch('thrift_cli.ThriftParser._load_file')
    def test_parse(self, mock_load_file):
        mock_load_file.return_value = data.TEST_THRIFT_CONTENT
        tparser = ThriftParser()
        expected_tparse_result = data.TEST_THRIFT_PARSE_RESULT
        tparse_result = tparser.parse(data.TEST_THRIFT_PATH)
        self.assertEqual(tparse_result, expected_tparse_result)

    def test_parse_structs(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        expected_structs = data.TEST_THRIFT_STRUCTS
        structs = tparser._parse_structs()
        self.assertEqual(structs, expected_structs)

    def test_parse_services(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        expected_services = data.TEST_THRIFT_SERVICES
        services = tparser._parse_services()
        self.assertEqual(services, expected_services)

    def test_parse_enums(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        expected_enums = data.TEST_THRIFT_ENUMS
        enums = tparser._parse_enums()
        self.assertEqual(enums, expected_enums)

    def test_parse_endpoints_from_service_definition(self):
        tparser = ThriftParser()
        endpoints = tparser._parse_endpoints_from_service_definition(data.TEST_THRIFT_SERVICE_DEFINITION)
        expected_endpoints = data.TEST_THRIFT_SERVICE_ENDPOINTS
        self.assertEqual(endpoints, expected_endpoints)

    def test_parse_struct_definitions(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        expected_struct_definitions = {
            data.TEST_THRIFT_STRUCT_NAME: data.TEST_THRIFT_STRUCT_DEFINITION,
            data.TEST_THRIFT_STRUCT_NAME2: data.TEST_THRIFT_STRUCT_DEFINITION2
        }
        struct_definitions = tparser._parse_struct_definitions()
        self.assertEqual(struct_definitions, expected_struct_definitions)

    def test_parse_service_definitions(self):
        tparser = ThriftParser()
        tparser._thrift_content = data.TEST_THRIFT_CONTENT
        expected_service_definitions = {
            data.TEST_THRIFT_SERVICE_NAME: data.TEST_THRIFT_SERVICE_DEFINITION,
            data.TEST_THRIFT_SERVICE_NAME2: data.TEST_THRIFT_SERVICE_DEFINITION2
        }
        service_definitions = tparser._parse_service_definitions()
        self.assertEqual(service_definitions, expected_service_definitions)
