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

import os
import textwrap

from thriftcli import ThriftService, ThriftStruct, ThriftParseResult

TEST_SERVER_ADDRESS = 'localhost:9090'
TEST_SERVER_ADDRESS2 = 'http://www.somewebsite.net:12201/with/an/unused/path'
TEST_SERVER_ADDRESS3 = 'https://noport.com/with/an/unused/path?and=parameters'
TEST_SERVER_HOSTNAME = 'localhost'
TEST_SERVER_HOSTNAME2 = 'www.somewebsite.net'
TEST_SERVER_HOSTNAME3 = 'noport.com'
TEST_SERVER_PORT = 9090
TEST_SERVER_PORT2 = 12201
TEST_SERVER_PORT3 = None
TEST_CERTIFICATE_VERIFICATION_DEFAULT_MODE = 'required'
TEST_CERTIFICATE_VERIFICATION_NONE_MODE = 'none'
TEST_THRIFT_DIR = 'somefolder'
TEST_THRIFT_FILE = 'Something.thrift'
TEST_THRIFT_PATH = '%s/%s' % (TEST_THRIFT_DIR, TEST_THRIFT_FILE)
TEST_THRIFT_MODULE_PATH = 'gen-py/Something'
TEST_THRIFT_MODULE_NAME = 'Something'
TEST_THRIFT_NAMESPACE = 'Something'
TEST_THRIFT_NAMESPACE2 = 'Something2'
TEST_THRIFT_ENUM_NAME = 'SomeEnum'
TEST_THRIFT_ENUM_NAME2 = 'SomeEnum2'
TEST_THRIFT_ENUM_REFERENCE = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_ENUM_NAME)
TEST_THRIFT_ENUM_REFERENCE2 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_ENUM_NAME2)
TEST_THRIFT_TYPEDEF_ALIAS_NAME = 'UserId'
TEST_THRIFT_TYPEDEF_ALIAS_NAME2 = 'MapType'
TEST_THRIFT_TYPEDEF_ALIAS_NAME3 = 'SomeStructs'
TEST_THRIFT_TYPEDEF_ALIAS_NAME4 = 'UserIdentifier'
TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_TYPEDEF_ALIAS_NAME)
TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_TYPEDEF_ALIAS_NAME2)
TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE3 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_TYPEDEF_ALIAS_NAME3)
TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE4 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_TYPEDEF_ALIAS_NAME4)
TEST_THRIFT_STRUCT_NAME = 'SomeStruct'
TEST_THRIFT_STRUCT_NAME2 = 'SomeStruct2'
TEST_THRIFT_STRUCT_NAME3 = 'SomeStruct3'
TEST_THRIFT_STRUCT_REFERENCE = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_STRUCT_NAME)
TEST_THRIFT_STRUCT_REFERENCE2 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_STRUCT_NAME2)
TEST_THRIFT_STRUCT_REFERENCE3 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_STRUCT_NAME3)
TEST_THRIFT_SERVICE_NAME = 'SomeService'
TEST_THRIFT_SERVICE_NAME2 = 'SomeService2'
TEST_THRIFT_SERVICE_NAME3 = 'SomeService3'
TEST_THRIFT_SERVICE_REFERENCE = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_SERVICE_NAME)
TEST_THRIFT_SERVICE_REFERENCE2 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_SERVICE_NAME2)
TEST_THRIFT_SERVICE_REFERENCE3 = '%s.%s' % (TEST_THRIFT_NAMESPACE, TEST_THRIFT_SERVICE_NAME3)
TEST_THRIFT_PY_NAMESPACE = "org.thrift.%s" % TEST_THRIFT_NAMESPACE
TEST_THRIFT_PY_NAMESPACE2 = "org.thrift.%s" % TEST_THRIFT_NAMESPACE2
TEST_THRIFT_PY_NAMESPACE_DEFINITION = "namespace py %s" % TEST_THRIFT_PY_NAMESPACE
TEST_THRIFT_PY_NAMESPACE_DEFINITION2 = "namespace py %s" % TEST_THRIFT_PY_NAMESPACE2

TEST_THRIFT_ENUM_DEFINITION = textwrap.dedent("""\
    enum %s {
        A,
        B,
        C,
        D
    }""" % TEST_THRIFT_ENUM_NAME)
TEST_THRIFT_ENUM_DEFINITION2 = textwrap.dedent("""\
    enum %s {
        W,
        X = 4,
        Y = 0xf2a,
        Z
    }""" % TEST_THRIFT_ENUM_NAME2)
TEST_THRIFT_TYPEDEF_DEFINITION = 'typedef i64 %s' % TEST_THRIFT_TYPEDEF_ALIAS_NAME
TEST_THRIFT_TYPEDEF_DEFINITION2 = 'typedef map<string, string> %s' % TEST_THRIFT_TYPEDEF_ALIAS_NAME2
TEST_THRIFT_TYPEDEF_DEFINITION3 = 'typedef list<%s> %s' % (TEST_THRIFT_STRUCT_NAME, TEST_THRIFT_TYPEDEF_ALIAS_NAME3)
TEST_THRIFT_TYPEDEF_DEFINITION4 = 'typedef %s %s' % (TEST_THRIFT_TYPEDEF_ALIAS_NAME, TEST_THRIFT_TYPEDEF_ALIAS_NAME4)
TEST_THRIFT_TYPEDEFS = {
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE: 'i64',
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2: 'map<string, string>',
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE3: 'list<%s>' % TEST_THRIFT_STRUCT_REFERENCE,
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE4: TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE
}
TEST_THRIFT_NAMESPACES = {
    TEST_THRIFT_NAMESPACE: TEST_THRIFT_PY_NAMESPACE
}
TEST_THRIFT_UNALIASED_TYPES = {
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE: 'i64',
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2: 'map<string, string>',
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE3: 'list<%s>' % TEST_THRIFT_STRUCT_REFERENCE,
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE4: 'i64'
}

TEST_THRIFT_STRUCT_FIELDS = {
    'thing_one': ThriftStruct.Field(1, 'string', 'thing_one'),
    'thing_two': ThriftStruct.Field(2, 'double', 'thing_two', default='2.0'),
    'thing_three': ThriftStruct.Field(3, 'bool', 'thing_three', default='False')
}
TEST_THRIFT_STRUCT_FIELDS2 = {
    'thing_one': ThriftStruct.Field(1, 'i8', 'thing_one', required=True),
    'thing_two': ThriftStruct.Field(2, 'i16', 'thing_two', required=False),
    'thing_three': ThriftStruct.Field(3, 'i32', 'thing_three', optional=True),
    'thing_four': ThriftStruct.Field(4, 'i64', 'thing_four', optional=False, default='0'),
    'thing_five': ThriftStruct.Field(5, 'binary', 'thing_five', required=True, optional=False),
    'thing_six': ThriftStruct.Field(6, 'byte', 'thing_six', required=False, optional=True)
}
TEST_THRIFT_STRUCT_FIELDS3 = {
    'thing_one': ThriftStruct.Field(1, 'list<string>', 'thing_one', required=True),
    'thing_two': ThriftStruct.Field(2, 'set<i8>', 'thing_two', optional=True),
    'thing_three': ThriftStruct.Field(3, 'map<string, string>', 'thing_three', required=True),
    'thing_four': ThriftStruct.Field(4, 'list<%s>' % TEST_THRIFT_STRUCT_REFERENCE, 'thing_four'),
    'thing_five': ThriftStruct.Field(5, 'map<%s, %s>' % (TEST_THRIFT_STRUCT_REFERENCE, TEST_THRIFT_STRUCT_REFERENCE2),
                                     'thing_five'),
    'thing_six': ThriftStruct.Field(6, 'set<list<%s>>' % TEST_THRIFT_STRUCT_REFERENCE2, 'thing_six')
}
TEST_THRIFT_STRUCT_DEFINITION = textwrap.dedent("""\
    struct %s {
        string thing_one,
        double thing_two = 2.0,
        bool thing_three = False;
    }""" % TEST_THRIFT_STRUCT_NAME)
TEST_THRIFT_STRUCT_DEFINITION2 = textwrap.dedent("""\
    struct %s {
        1:required i8 thing_one,
        2:i16 thing_two,
        3:optional i32 thing_three,
        4:required i64 thing_four = 0,
        5:required binary thing_five,
        6:optional byte thing_six
    }""" % TEST_THRIFT_STRUCT_NAME2)
TEST_THRIFT_STRUCT_DEFINITION3 = textwrap.dedent("""\
    struct %s {
        1:required list<string> thing_one,
        2:optional set<i8> thing_two,
        3:required map<string, string> thing_three,
        4:list<%s> thing_four,
        5:map<%s, %s> thing_five,
        6:set<list<%s>> thing_six
    }""" % (TEST_THRIFT_STRUCT_NAME3,
            TEST_THRIFT_STRUCT_NAME,
            TEST_THRIFT_STRUCT_NAME,
            TEST_THRIFT_STRUCT_NAME2,
            TEST_THRIFT_STRUCT_NAME2))
TEST_THRIFT_STRUCT = ThriftStruct(TEST_THRIFT_STRUCT_REFERENCE, TEST_THRIFT_STRUCT_FIELDS)
TEST_THRIFT_STRUCT2 = ThriftStruct(TEST_THRIFT_STRUCT_REFERENCE2, TEST_THRIFT_STRUCT_FIELDS2)
TEST_THRIFT_STRUCT3 = ThriftStruct(TEST_THRIFT_STRUCT_REFERENCE3, TEST_THRIFT_STRUCT_FIELDS3)
TEST_THRIFT_SERVICE_ENDPOINTS = {
    'ping': ThriftService.Endpoint('void', 'ping'),
    'doSomething1': ThriftService.Endpoint('i32', 'doSomething1', {
        'num1': ThriftStruct.Field(1, 'i32', 'num1'),
        'num2': ThriftStruct.Field(2, 'i32', 'num2'),
        'op': ThriftStruct.Field(3, TEST_THRIFT_ENUM_REFERENCE, 'op')
    }),
    'useSomeStruct': ThriftService.Endpoint('void', 'useSomeStruct', {
        'someStruct': ThriftStruct.Field(1, TEST_THRIFT_STRUCT_REFERENCE, 'someStruct')
    }, oneway=True)
}
TEST_THRIFT_SERVICE_ENDPOINTS2 = {
    'ping': ThriftService.Endpoint('void', 'ping'),
    'doSomething2': ThriftService.Endpoint('string', 'doSomething2', {
        'num1': ThriftStruct.Field(1, 'i32', 'num1')
    }),
    'useSomeStruct2': ThriftService.Endpoint('void', 'useSomeStruct2', {
        'someStruct': ThriftStruct.Field(1, TEST_THRIFT_STRUCT_REFERENCE2, 'someStruct')
    })
}
TEST_THRIFT_SERVICE_ENDPOINTS3 = TEST_THRIFT_SERVICE_ENDPOINTS.copy()
TEST_THRIFT_SERVICE_ENDPOINTS3.update({
    'ping': ThriftService.Endpoint('void', 'ping'),
    'passMap': ThriftService.Endpoint(TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2, 'passMap', {
        'myMap': ThriftStruct.Field(1, TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2, 'myMap')
    }),
    'passSetOfLists': ThriftService.Endpoint('set<list<%s>>' % TEST_THRIFT_STRUCT_REFERENCE, 'passSetOfLists', {
        'setOfLists': ThriftStruct.Field(1, 'set<list<%s>>' % TEST_THRIFT_STRUCT_REFERENCE, 'setOfLists')
    })
})
TEST_THRIFT_SERVICE_DEFINITION = textwrap.dedent("""\
    service %s {
        void ping(),
        i32 doSomething1(i32 num1, i32 num2, %s op),
        oneway void useSomeStruct(1:SomeStruct someStruct);
    }""" % (TEST_THRIFT_SERVICE_NAME, TEST_THRIFT_ENUM_NAME))
TEST_THRIFT_SERVICE_DEFINITION2 = textwrap.dedent("""\
    service %s {
        void ping(),
        string doSomething2(1:i32 num1),
        void useSomeStruct2(1:SomeStruct2 someStruct)
    }""" % TEST_THRIFT_SERVICE_NAME2)
TEST_THRIFT_SERVICE_DEFINITION3 = textwrap.dedent("""\
    service %s extends %s {
        void ping(),
        MapType passMap(1:MapType myMap),
        set<list<%s>> passSetOfLists(1:set<list<%s>> setOfLists)
    }""" % (TEST_THRIFT_SERVICE_NAME3, TEST_THRIFT_SERVICE_NAME, TEST_THRIFT_STRUCT_NAME, TEST_THRIFT_STRUCT_NAME))
TEST_JSON_TO_CONVERT = {
    "num1": 3,
    "num2": 4,
    "op": "A"
}
TEST_JSON_TO_CONVERT2 = {
    "myMap": {
        "key": "value",
        "key2": "value2",
        "key3": "value3"
    }
}
TEST_JSON_TO_CONVERT3 = {
    "setOfLists": [
        [{
            "thing_one": '1',
            "thing_two": 2.000,
            "thing_three": True,
        }, {
            "thing_one": '2',
            "thing_two": 2.00,
            "thing_three": False,
        }
        ],
        [{
            "thing_one": '3',
            "thing_two": 2.0,
            "thing_three": True,
        }]
    ]
}
TEST_THRIFT_SERVICE = ThriftService(TEST_THRIFT_SERVICE_REFERENCE, TEST_THRIFT_SERVICE_ENDPOINTS, None)
TEST_THRIFT_SERVICE2 = ThriftService(TEST_THRIFT_SERVICE_REFERENCE2, TEST_THRIFT_SERVICE_ENDPOINTS2, None)
TEST_THRIFT_SERVICE3 = ThriftService(
    TEST_THRIFT_SERVICE_REFERENCE3,
    TEST_THRIFT_SERVICE_ENDPOINTS3,
    TEST_THRIFT_SERVICE_REFERENCE)
TEST_THRIFT_REFERENCES = {
    TEST_THRIFT_ENUM_REFERENCE,
    TEST_THRIFT_ENUM_REFERENCE2,
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE,
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE2,
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE3,
    TEST_THRIFT_TYPEDEF_ALIAS_REFERENCE4,
    TEST_THRIFT_STRUCT_REFERENCE,
    TEST_THRIFT_STRUCT_REFERENCE2,
    TEST_THRIFT_STRUCT_REFERENCE3,
    TEST_THRIFT_SERVICE_REFERENCE,
    TEST_THRIFT_SERVICE_REFERENCE2,
    TEST_THRIFT_SERVICE_REFERENCE3
}
TEST_THRIFT_CONTENT = '\n'.join([
    TEST_THRIFT_PY_NAMESPACE_DEFINITION,
    TEST_THRIFT_ENUM_DEFINITION,
    TEST_THRIFT_ENUM_DEFINITION2,
    TEST_THRIFT_TYPEDEF_DEFINITION,
    TEST_THRIFT_TYPEDEF_DEFINITION2,
    TEST_THRIFT_TYPEDEF_DEFINITION3,
    TEST_THRIFT_TYPEDEF_DEFINITION4,
    TEST_THRIFT_STRUCT_DEFINITION,
    TEST_THRIFT_STRUCT_DEFINITION2,
    TEST_THRIFT_STRUCT_DEFINITION3,
    TEST_THRIFT_SERVICE_DEFINITION,
    TEST_THRIFT_SERVICE_DEFINITION2,
    TEST_THRIFT_SERVICE_DEFINITION3
])
TEST_THRIFT_CIRCULAR_TYPEDEF_DEFINITION = 'typedef Circular Circular2'
TEST_THRIFT_CIRCULAR_TYPEDEF_DEFINITION2 = 'typedef Circular2 Circular3'
TEST_THRIFT_CIRCULAR_TYPEDEF_DEFINITION3 = 'typedef Circular3 Circular'
TEST_THRIFT_CIRCULAR_TYPEDEFS = {
    '%s.Circular2' % TEST_THRIFT_NAMESPACE: '%s.Circular' % TEST_THRIFT_NAMESPACE,
    '%s.Circular3' % TEST_THRIFT_NAMESPACE: '%s.Circular2' % TEST_THRIFT_NAMESPACE,
    '%s.Circular' % TEST_THRIFT_NAMESPACE: '%s.Circular3' % TEST_THRIFT_NAMESPACE
}
TEST_THRIFT_CONTENT_CIRCULAR_TYPEDEFS = '\n'.join([
    TEST_THRIFT_CIRCULAR_TYPEDEF_DEFINITION,
    TEST_THRIFT_CIRCULAR_TYPEDEF_DEFINITION2,
    TEST_THRIFT_CIRCULAR_TYPEDEF_DEFINITION3
])
TEST_THRIFT_STRUCTS = {
    TEST_THRIFT_STRUCT_REFERENCE: TEST_THRIFT_STRUCT,
    TEST_THRIFT_STRUCT_REFERENCE2: TEST_THRIFT_STRUCT2,
    TEST_THRIFT_STRUCT_REFERENCE3: TEST_THRIFT_STRUCT3
}
TEST_THRIFT_SERVICES = {
    TEST_THRIFT_SERVICE_REFERENCE: TEST_THRIFT_SERVICE,
    TEST_THRIFT_SERVICE_REFERENCE2: TEST_THRIFT_SERVICE2,
    TEST_THRIFT_SERVICE_REFERENCE3: TEST_THRIFT_SERVICE3
}
TEST_THRIFT_ENUMS = {TEST_THRIFT_ENUM_REFERENCE, TEST_THRIFT_ENUM_REFERENCE2}
TEST_THRIFT_PARSE_RESULT = ThriftParseResult(
    TEST_THRIFT_STRUCTS, TEST_THRIFT_SERVICES, TEST_THRIFT_ENUMS, TEST_THRIFT_TYPEDEFS,
    TEST_THRIFT_NAMESPACES)
TEST_THRIFT_INCLUDE_STATEMENT = 'include "Included.thrift"'
TEST_THRIFT_INCLUDED_NAMESPACE = 'Included'
TEST_THRIFT_INCLUDED_ENUM_NAME = 'SomeIncludedEnum'
TEST_THRIFT_INCLUDED_ENUM_DEFINITION = textwrap.dedent("""\
    enum %s {
        THIS_STUFF,
        THAT_STUFF,
        MORE_STUFF
    }""" % TEST_THRIFT_INCLUDED_ENUM_NAME)
TEST_THRIFT_INCLUDED_ENUM_REFERENCE = '%s.%s' % (TEST_THRIFT_INCLUDED_NAMESPACE, TEST_THRIFT_INCLUDED_ENUM_NAME)
TEST_THRIFT_INCLUDED_STRUCT_NAME = 'SomeIncludedStruct'
TEST_THRIFT_INCLUDED_STRUCT_REFERENCE = '%s.%s' % (TEST_THRIFT_INCLUDED_NAMESPACE, TEST_THRIFT_INCLUDED_STRUCT_NAME)
TEST_THRIFT_INCLUDED_STRUCT_DEFINITION = textwrap.dedent("""\
    struct %s {
        1:string some_string,
        2:%s my_enum
    }
""" % (TEST_THRIFT_INCLUDED_STRUCT_NAME, TEST_THRIFT_INCLUDED_ENUM_NAME))
TEST_THRIFT_INCLUDED_STRUCT_FIELDS = {
    'some_string': ThriftStruct.Field(1, 'string', 'some_string'),
    'my_enum': ThriftStruct.Field(2, TEST_THRIFT_INCLUDED_ENUM_REFERENCE, 'my_enum')
}
TEST_THRIFT_INCLUDED_STRUCT = ThriftStruct('%s.%s' % (TEST_THRIFT_INCLUDED_NAMESPACE, TEST_THRIFT_INCLUDED_STRUCT_NAME),
                                           TEST_THRIFT_INCLUDED_STRUCT_FIELDS)
TEST_THRIFT_INCLUDED_SERVICE_NAME = 'SomeIncludedService'
TEST_THRIFT_INCLUDED_SERVICE_REFERENCE = '%s.%s' % (TEST_THRIFT_INCLUDED_NAMESPACE, TEST_THRIFT_INCLUDED_SERVICE_NAME)
TEST_THRIFT_INCLUDED_SERVICE_DEFINITION = textwrap.dedent("""\
    service %s {
        %s passSomeStuff(1:%s someStuff),
    }""" % (
    TEST_THRIFT_INCLUDED_SERVICE_NAME, TEST_THRIFT_INCLUDED_STRUCT_NAME, TEST_THRIFT_INCLUDED_STRUCT_NAME))
TEST_THRIFT_INCLUDED_SERVICE_ENDPOINTS = {
    'passSomeStuff': ThriftService.Endpoint(TEST_THRIFT_INCLUDED_STRUCT_REFERENCE, 'passSomeStuff', {
        'someStuff': ThriftStruct.Field(1, TEST_THRIFT_INCLUDED_STRUCT_REFERENCE, 'someStuff')
    })
}
TEST_THRIFT_INCLUDED_SERVICE = ThriftService(TEST_THRIFT_INCLUDED_SERVICE_REFERENCE,
                                             TEST_THRIFT_INCLUDED_SERVICE_ENDPOINTS,
                                             None)
TEST_THRIFT_INCLUDED_STRUCTS = {
    TEST_THRIFT_INCLUDED_STRUCT_REFERENCE: TEST_THRIFT_INCLUDED_STRUCT
}
TEST_THRIFT_INCLUDED_SERVICES = {
    TEST_THRIFT_INCLUDED_SERVICE_REFERENCE: TEST_THRIFT_INCLUDED_SERVICE
}
TEST_THRIFT_INCLUDED_ENUMS = {TEST_THRIFT_INCLUDED_ENUM_REFERENCE}
TEST_THRIFT_INCLUDED_TYPEDEF_DEFINITION = 'typedef i64 Id'
TEST_THRIFT_INCLUDED_TYPEDEF_DEFINITION2 = 'typedef list<Id> Ids'
TEST_THRIFT_INCLUDED_TYPEDEFS = {
    '%s.Id' % TEST_THRIFT_INCLUDED_NAMESPACE: 'i64',
    '%s.Ids' % TEST_THRIFT_INCLUDED_NAMESPACE: 'list<%s.Id>' % TEST_THRIFT_INCLUDED_NAMESPACE,
}
TEST_THRIFT_INCLUDED_PARSE_RESULT = ThriftParseResult(TEST_THRIFT_INCLUDED_STRUCTS, TEST_THRIFT_INCLUDED_SERVICES,
                                                      TEST_THRIFT_INCLUDED_ENUMS, TEST_THRIFT_INCLUDED_TYPEDEFS)
TEST_THRIFT_INCLUDED_CONTENT = '\n'.join([
    TEST_THRIFT_PY_NAMESPACE_DEFINITION2,
    TEST_THRIFT_INCLUDED_ENUM_DEFINITION,
    TEST_THRIFT_INCLUDED_TYPEDEF_DEFINITION,
    TEST_THRIFT_INCLUDED_TYPEDEF_DEFINITION2,
    TEST_THRIFT_INCLUDED_STRUCT_DEFINITION,
    TEST_THRIFT_INCLUDED_SERVICE_DEFINITION
])
TEST_THRIFT_INCLUDING_NAMESPACE = 'Including'
TEST_THRIFT_INCLUDING_ENUM_NAME = 'SomeIncludingEnum'
TEST_THRIFT_INCLUDING_ENUM_DEFINITION = textwrap.dedent("""\
    enum %s {
        ONE,
        TWO,
        THREE
    }""" % TEST_THRIFT_INCLUDING_ENUM_NAME)
TEST_THRIFT_INCLUDING_ENUM_REFERENCE = '%s.%s' % (TEST_THRIFT_INCLUDING_NAMESPACE, TEST_THRIFT_INCLUDING_ENUM_NAME)
TEST_THRIFT_INCLUDING_ENUMS = {TEST_THRIFT_INCLUDED_ENUM_REFERENCE, TEST_THRIFT_INCLUDING_ENUM_REFERENCE}
TEST_THRIFT_INCLUDING_STRUCT_NAME = 'SomeIncludingStruct'
TEST_THRIFT_INCLUDING_STRUCT_REFERENCE = '%s.%s' % (TEST_THRIFT_INCLUDING_NAMESPACE, TEST_THRIFT_INCLUDING_STRUCT_NAME)
TEST_THRIFT_INCLUDING_STRUCT_DEFINITION = textwrap.dedent("""\
    struct %s {
        1:%s included_enum,
        2:%s included_struct,
        3:%s my_enum,
        4:%s included_typedef
    }""" % (TEST_THRIFT_INCLUDING_STRUCT_NAME, TEST_THRIFT_INCLUDED_ENUM_REFERENCE,
            TEST_THRIFT_INCLUDED_STRUCT_REFERENCE, TEST_THRIFT_INCLUDING_ENUM_NAME,
            TEST_THRIFT_INCLUDED_TYPEDEF_DEFINITION2))
TEST_THRIFT_INCLUDING_STRUCT_FIELDS = {
    'included_enum': ThriftStruct.Field(1, TEST_THRIFT_INCLUDED_ENUM_REFERENCE, 'included_enum'),
    'included_struct': ThriftStruct.Field(2, TEST_THRIFT_INCLUDED_STRUCT_REFERENCE, 'included_struct'),
    'my_enum': ThriftStruct.Field(3, TEST_THRIFT_INCLUDING_ENUM_REFERENCE, 'my_enum'),
    'included_typedef': ThriftStruct.Field(4, TEST_THRIFT_INCLUDED_TYPEDEF_DEFINITION2, 'included_typedef')
}
TEST_THRIFT_INCLUDING_STRUCT = ThriftStruct(TEST_THRIFT_INCLUDING_STRUCT_REFERENCE, TEST_THRIFT_INCLUDING_STRUCT_FIELDS)
TEST_THRIFT_INCLUDING_SERVICE_NAME = 'SomeIncludingService'
TEST_THRIFT_INCLUDING_SERVICE_REFERENCE = '%s.%s' % (TEST_THRIFT_INCLUDING_NAMESPACE,
                                                     TEST_THRIFT_INCLUDING_SERVICE_NAME)
TEST_THRIFT_INCLUDING_SERVICE_DEFINITION = textwrap.dedent("""\
    service %s extends %s {
        %s passIncludedStruct(1:%s includedStruct),
        %s passMyStruct(1:%s myStruct),
    }""" % (TEST_THRIFT_INCLUDING_SERVICE_NAME, TEST_THRIFT_INCLUDED_SERVICE_REFERENCE,
            TEST_THRIFT_INCLUDED_STRUCT_REFERENCE, TEST_THRIFT_INCLUDED_STRUCT_REFERENCE,
            TEST_THRIFT_INCLUDING_STRUCT_NAME, TEST_THRIFT_INCLUDING_STRUCT_NAME))
TEST_THRIFT_INCLUDING_SERVICE_ENDPOINTS = TEST_THRIFT_INCLUDED_SERVICE_ENDPOINTS.copy()
TEST_THRIFT_INCLUDING_SERVICE_ENDPOINTS.update({
    'passIncludedStruct': ThriftService.Endpoint(
        TEST_THRIFT_INCLUDED_STRUCT_REFERENCE,
        'passIncludedStruct',
        {
            'includedStruct': ThriftStruct.Field(
                1, TEST_THRIFT_INCLUDED_STRUCT_REFERENCE, 'includedStruct')
        }),
    'passMyStruct': ThriftService.Endpoint(
        TEST_THRIFT_INCLUDING_STRUCT_REFERENCE,
        'passMyStruct',
        {
            'myStruct': ThriftStruct.Field(
                1, TEST_THRIFT_INCLUDING_STRUCT_REFERENCE, 'myStruct')
        })
})
TEST_THRIFT_INCLUDING_SERVICE = ThriftService(TEST_THRIFT_INCLUDING_SERVICE_REFERENCE,
                                              TEST_THRIFT_INCLUDING_SERVICE_ENDPOINTS,
                                              TEST_THRIFT_INCLUDED_SERVICE_REFERENCE)
TEST_THRIFT_INCLUDING_SERVICES = {
    TEST_THRIFT_INCLUDED_SERVICE_REFERENCE: TEST_THRIFT_INCLUDED_SERVICE,
    TEST_THRIFT_INCLUDING_SERVICE_REFERENCE: TEST_THRIFT_INCLUDING_SERVICE
}
TEST_THRIFT_INCLUDING_STRUCTS = {
    TEST_THRIFT_INCLUDED_STRUCT_REFERENCE: TEST_THRIFT_INCLUDED_STRUCT,
    TEST_THRIFT_INCLUDING_STRUCT_REFERENCE: TEST_THRIFT_INCLUDING_STRUCT
}
TEST_THRIFT_INCLUDING_TYPEDEF_DEFINITION = 'typedef bool Bool'
TEST_THRIFT_INCLUDING_TYPEDEFS = {
    '%s.Bool' % TEST_THRIFT_INCLUDING_NAMESPACE: 'bool'
}
TEST_THRIFT_INCLUDING_TYPEDEFS.update(TEST_THRIFT_INCLUDED_TYPEDEFS.copy())
TEST_THRIFT_INCLUDING_NAMESPACES = {
    TEST_THRIFT_INCLUDING_NAMESPACE: TEST_THRIFT_INCLUDING_NAMESPACE,
    TEST_THRIFT_INCLUDED_NAMESPACE: TEST_THRIFT_PY_NAMESPACE2
}
TEST_THRIFT_INCLUDING_PARSE_RESULT = ThriftParseResult(TEST_THRIFT_INCLUDING_STRUCTS, TEST_THRIFT_INCLUDING_SERVICES,
                                                       TEST_THRIFT_INCLUDING_ENUMS, TEST_THRIFT_INCLUDING_TYPEDEFS,
                                                       TEST_THRIFT_INCLUDING_NAMESPACES)
TEST_THRIFT_INCLUDING_PATH = '%s/Including.thrift' % TEST_THRIFT_DIR
TEST_THRIFT_DIR_PATH = 'target/folder/'
TEST_KEY_FILE_PATH = 'target/folder/keystore.pem'
TEST_THRIFT_DIR_PATH2 = 'other/target/folder'
TEST_THRIFT_INCLUDED_PATH = 'target/folder/Included.thrift'
TEST_THRIFT_INCLUDING_CONTENT = '\n'.join([
    TEST_THRIFT_INCLUDE_STATEMENT,
    TEST_THRIFT_INCLUDING_ENUM_DEFINITION,
    TEST_THRIFT_INCLUDING_TYPEDEF_DEFINITION,
    TEST_THRIFT_INCLUDING_STRUCT_DEFINITION,
    TEST_THRIFT_INCLUDING_SERVICE_DEFINITION
])
TEST_THRIFT_ENDPOINT_NAME = 'SomeService.useSomeStruct'
TEST_THRIFT_METHOD_NAME = 'useSomeStruct'
TEST_JSON_PATH = '/path/to/json.json'
TEST_JSON_REQUEST_BODY = '{"request": {"num": 1, "text": "some text", "seq": [1, 2, 3]}, "id": 0}'
TEST_JSON_REQUEST_BODY2 = '{"num": 1, "text": "some text", "seq": [1, 2, 3]}'
TEST_JSON_REQUEST_BODY3 = '{"request": {"animal": {"type": "GIRAFFE", "name": "giraffee"}}}'
TEST_JSON_REQUEST_BODY4 = '{"work": {"num1": 1, "num2": 2, "extra": {"more": 1, "attributes": 2}}}'
TEST_JAVA_THRIFT_REQUEST_BODY = 'request:MyRequest(num:1,text:some text,seq:[1,2,3]), id:0'
TEST_JAVA_THRIFT_REQUEST_BODY2 = 'MyRequest(num:1,text:some text,seq:[1,2,3])'
TEST_JAVA_THRIFT_REQUEST_BODY3 = 'request:AnimalsCreateRequest(animal:Animal(id:null, type:GIRAFFE, name:giraffee))'
TEST_JAVA_THRIFT_REQUEST_BODY4 = 'work:Work(num1:1, num2:2, extra: Extra(more:1, attributes:2))'
TEST_INVALID_REQUEST_BODY = 'nonsense'
TEST_ARGUMENT_DICTIONARY = {"request": {"num": 1, "text": "some text", "seq": [1, 2, 3]}, "id": 0}
TEST_ARGUMENT_DICTIONARY2 = {"num": 1, "text": "some text", "seq": [1, 2, 3]}
TEST_ARGUMENT_DICTIONARY3 = {"request": {"animal": {"id": None, "type": "GIRAFFE", "name": "giraffee"}}}
TEST_ARGUMENT_DICTIONARY3_ALT = {"request": {"animal": {"type": "GIRAFFE", "name": "giraffee"}}}
TEST_ARGUMENT_DICTIONARY4 = {"work": {"num1": 1, "num2": 2, "extra": {"more": 1, "attributes": 2}}}
TEST_CLI_NAME = 'thriftcli'
TEST_ZOOKEEPER_PATH = '/some_path'
TEST_ZOOKEEPER_CHILD_NAME = 'member_0000000041'
TEST_ZOOKEEPER_SERVER_ADDRESS = '%s:%s/%s' % (TEST_SERVER_HOSTNAME, TEST_SERVER_PORT, TEST_ZOOKEEPER_PATH)
TEST_ZOOKEEPER_CHILD_PATH = os.path.join(TEST_ZOOKEEPER_PATH, TEST_ZOOKEEPER_CHILD_NAME)
TEST_ZNODE = ('{"additionalEndpoints": {"%s": {"host": "%s", "port": %s}}, "status": "ALIVE", "shard": 0}' %
              (TEST_THRIFT_SERVICE_NAME, TEST_SERVER_HOSTNAME2, TEST_SERVER_PORT2),
              None)
TEST_CLIENT_ID = "client_abc"
TEST_PROXY = "proxy.abc.com:12345"
TEST_CLI_ARGS = [TEST_CLI_NAME, TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH, '-p', TEST_PROXY]
TEST_CLI_ARGS2 = [TEST_CLI_NAME, TEST_ZOOKEEPER_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                  '-b', TEST_JSON_PATH, '-z', '-j', '-c', '-i', TEST_CLIENT_ID]
TEST_CLI_ARGS3 = [TEST_CLI_NAME, TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                  '-I', TEST_THRIFT_DIR_PATH, TEST_THRIFT_DIR_PATH2, '--proxy', TEST_PROXY]
TEST_CLI_ARGS4 = [TEST_CLI_NAME, TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                  '--body', TEST_JSON_REQUEST_BODY, '--include', TEST_THRIFT_DIR_PATH, TEST_THRIFT_DIR_PATH2,
                  '--client_id', TEST_CLIENT_ID]
TEST_CLI_ARGS5 = [TEST_CLI_NAME, TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                  '--body', TEST_INVALID_REQUEST_BODY]
TEST_CLI_ARGS6 = [TEST_CLI_NAME, TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                  '--body', TEST_JSON_REQUEST_BODY, '--include', TEST_THRIFT_DIR_PATH, TEST_THRIFT_DIR_PATH2,
                  '--client_id', TEST_CLIENT_ID, '--tls', '--tls_key_path', TEST_KEY_FILE_PATH, '--cert_verification_mode',
                  TEST_CERTIFICATE_VERIFICATION_NONE_MODE]
TEST_PARSED_ARGS = (TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH, [], {}, False, False, False, None, TEST_PROXY, False, None,
                    TEST_CERTIFICATE_VERIFICATION_DEFAULT_MODE)
TEST_PARSED_ARGS2 = (TEST_ZOOKEEPER_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH, [],
                     TEST_ARGUMENT_DICTIONARY, True, True, True, TEST_CLIENT_ID, None, False, None, TEST_CERTIFICATE_VERIFICATION_DEFAULT_MODE)
TEST_PARSED_ARGS3 = (TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                     [TEST_THRIFT_DIR_PATH, TEST_THRIFT_DIR_PATH2], {}, False, False, False, None, TEST_PROXY, False, None,
                     TEST_CERTIFICATE_VERIFICATION_DEFAULT_MODE)
TEST_PARSED_ARGS4 = (TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                     [TEST_THRIFT_DIR_PATH, TEST_THRIFT_DIR_PATH2], TEST_ARGUMENT_DICTIONARY, False, False, False, TEST_CLIENT_ID, None, False, None,
                     TEST_CERTIFICATE_VERIFICATION_DEFAULT_MODE)
TEST_PARSED_ARGS6 = (TEST_SERVER_ADDRESS, TEST_THRIFT_ENDPOINT_NAME, TEST_THRIFT_PATH,
                     [TEST_THRIFT_DIR_PATH, TEST_THRIFT_DIR_PATH2], TEST_ARGUMENT_DICTIONARY, False, False, False, TEST_CLIENT_ID, None, True,
                     TEST_KEY_FILE_PATH, TEST_CERTIFICATE_VERIFICATION_NONE_MODE)
