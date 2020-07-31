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

from thriftcli import ThriftUnion, ThriftStruct, ThriftCLIError


class TestThriftUnion(unittest.TestCase):
    def test_ne(self):
        union1 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'void', 'someField1')})
        union2 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'i32', 'someField1')})
        struct1 = ThriftStruct("struct1", {"someField1": ThriftStruct.Field(1, 'void', 'someField1', required=False)})
        union3 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'void', 'someField1')})
        self.assertTrue(union1 != union2)
        self.assertTrue(union1 != struct1)
        self.assertFalse(union1 != union3)

    def test_eq(self):
        union1 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'void', 'someField1')})
        union2 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'i32', 'someField1'),"someField2": ThriftUnion.Field(2, 'i16', 'someField3')})
        struct1 = ThriftStruct("struct1", {"someField1": ThriftStruct.Field(1, 'void', 'someField1', required=False)})
        union3 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'void', 'someField1')})
        self.assertFalse(union1 == union2)
        self.assertFalse(union1 == struct1)
        self.assertTrue(union1 == union3)

    def test_str(self):
        union1 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'void', 'someField1')})
        union2 = ThriftUnion("union1", {"someField1": ThriftUnion.Field(1, 'i32', 'someField1'),"someField2": ThriftUnion.Field(2, 'i16', 'someField3')})
        self.assertEquals("union1", str(union1))
