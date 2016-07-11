import unittest
import data

from thriftcli.request_body_converter import convert


class TestRequestBodyConverter(unittest.TestCase):

    def test_json_request_body(self):
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY, convert(data.TEST_JSON_REQUEST_BODY))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY2, convert(data.TEST_JSON_REQUEST_BODY2))

    def test_java_thrift_request_body(self):
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY, convert(data.TEST_JAVA_THRIFT_REQUEST_BODY))
        self.assertEqual(data.TEST_ARGUMENT_DICTIONARY2, convert(data.TEST_JAVA_THRIFT_REQUEST_BODY2))

    def test_invalid_request_body(self):
        with self.assertRaises(ValueError):
            convert(data.TEST_INVALID_REQUEST_BODY)
