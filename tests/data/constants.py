from thrift_cli import ThriftService, ThriftStruct, ThriftParser
from thrift.Thrift import TType

TEST_SERVER_ADDRESS = 'localhost:9090'
TEST_SERVER_URL = 'localhost'
TEST_PORT = 9090
TEST_THRIFT_PATH = 'somefolder/something.thrift'
TEST_THRIFT_MODULE_PATH = 'gen-py/something'
TEST_THRIFT_MODULE_NAME = 'something'
TEST_THRIFT_STRUCT_NAME = 'SomeStruct'
TEST_THRIFT_STRUCT_NAME2 = 'SomeStruct2'
TEST_THRIFT_STRUCT_FIELDS = {
	'thing_one': ThriftStruct.Field(1, 'string', 'thing_one'),
	'thing_two': ThriftStruct.Field(2, 'double', 'thing_two', default=2.0),
	'thing_three': ThriftStruct.Field(3, 'bool', 'thing_three', default=False)
}
TEST_THRIFT_STRUCT_FIELDS2 = {
	'thing_one': ThriftStruct.Field(1, 'i8', 'thing_one', required=True),
	'thing_two': ThriftStruct.Field(2, 'i16', 'thing_two', required=False),
	'thing_three': ThriftStruct.Field(3, 'i32', 'thing_three', optional=True),
	'thing_four': ThriftStruct.Field(4, 'i64', 'thing_four', optional=False, default=0),
	'thing_five': ThriftStruct.Field(5, 'binary', 'thing_five', required=True, optional=False),
	'thing_six': ThriftStruct.Field(6, 'byte', 'thing_six', required=False, optional=True)
}
TEST_THRIFT_STRUCT_DEFINITION = ("""
	struct %s {
		1:string thing_one,
		2:double thing_two = 2.0,
		3:bool thing_three = False
	}""" % TEST_THRIFT_STRUCT_NAME).lstrip('\n')
TEST_THRIFT_STRUCT_DEFINITION2 = ("""
	struct %s {
		1:required i8 thing_one,
		2:i16 thing_two,
		3:optional i32 thing_three,
		4:required i64 thing_four = 0,
		5:required binary thing_five,
		6:optional byte thing_six
	}""" % TEST_THRIFT_STRUCT_NAME2).lstrip('\n')
TEST_THRIFT_STRUCT = ThriftStruct(TEST_THRIFT_STRUCT_NAME, TEST_THRIFT_STRUCT_FIELDS)
TEST_THRIFT_STRUCT2 = ThriftStruct(TEST_THRIFT_STRUCT_NAME2, TEST_THRIFT_STRUCT_FIELDS2)
TEST_THRIFT_SERVICE_NAME = 'SomeService'
TEST_THRIFT_SERVICE_NAME2 = 'SomeService2'
TEST_THRIFT_SERVICE_ENDPOINTS = {
	'ping': ThriftService.Endpoint('void', 'ping'),
	'doSomething1': ThriftService.Endpoint('i32', 'doSomething1', {
		'num1': ThriftStruct.Field(1, 'i32', 'num1'),
		'num2': ThriftStruct.Field(2, 'i32', 'num2'),
		'op': ThriftStruct.Field(3, 'Operation', 'op')
		}),
	'useSomeStruct': ThriftService.Endpoint('void', 'useSomeStruct', {
		'someStruct': ThriftStruct.Field(1, 'SomeStruct', 'someStruct')
		}, oneway=True)
}
TEST_THRIFT_SERVICE_ENDPOINTS2 = {
	'ping': ThriftService.Endpoint('void', 'ping'),
	'doSomething2': ThriftService.Endpoint('string', 'doSomething2', {
		'num1': ThriftStruct.Field(1, 'i32', 'num1')
		}),
	'useSomeStruct2': ThriftService.Endpoint('void', 'useSomeStruct2', {
		'someStruct': ThriftStruct.Field(1, 'SomeStruct2', 'someStruct')
		})
}
TEST_THRIFT_SERVICE_DEFINITION = ("""
	service %s {
		void ping(),
		i32 doSomething1(1:i32 num1, 2:i32 num2, 3:Operation op),
		oneway void useSomeStruct(1:SomeStruct someStruct)
	}""" % TEST_THRIFT_SERVICE_NAME).lstrip('\n')
TEST_THRIFT_SERVICE_DEFINITION2 = ("""
	service %s {
		void ping(),
		string doSomething2(1:i32 num1)
		void useSomeStruct2(1:SomeStruct2 someStruct)
	}""" % TEST_THRIFT_SERVICE_NAME2).lstrip('\n')
TEST_THRIFT_SERVICE = ThriftService(TEST_THRIFT_SERVICE_NAME, TEST_THRIFT_SERVICE_ENDPOINTS)
TEST_THRIFT_SERVICE2 = ThriftService(TEST_THRIFT_SERVICE_NAME2, TEST_THRIFT_SERVICE_ENDPOINTS2)
TEST_THRIFT_CONTENT = '\n'.join([
	TEST_THRIFT_STRUCT_DEFINITION,
	TEST_THRIFT_STRUCT_DEFINITION2,
	TEST_THRIFT_SERVICE_DEFINITION,
	TEST_THRIFT_SERVICE_DEFINITION2
	])
TEST_THRIFT_STRUCTS = {
	TEST_THRIFT_STRUCT_NAME: TEST_THRIFT_STRUCT,
	TEST_THRIFT_STRUCT_NAME2: TEST_THRIFT_STRUCT2
}
TEST_THRIFT_SERVICES = {
	TEST_THRIFT_SERVICE_NAME: TEST_THRIFT_SERVICE,
	TEST_THRIFT_SERVICE_NAME2: TEST_THRIFT_SERVICE2
}
TEST_THRIFT_PARSE_RESULT = ThriftParser.Result(TEST_THRIFT_STRUCTS, TEST_THRIFT_SERVICES)
TEST_JSON_CONTENT = """
	{
		"request": {
			"id": 0,
			"type": 0,
			"name": "giraffee",
			"weight": 2.0
		}
	}""".lstrip('\n')
TEST_JSON_OBJECT = {
	'request': {
		'id': 0,
		'type': 0,
		'name:': 'giraffee',
		'weight': 2.0
	}
}