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

from .thrift_cli_error import ThriftCLIError


class ThriftStruct(object):
    """ Provides a representation of a struct declared in thrift. """

    class Field(object):
        def __init__(self, index, field_type, name, **kwargs):
            try:
                self.index = int(index)
            except ValueError:
                self.index = None
            self.field_type = field_type
            self.name = name
            self.default = kwargs.get('default', None)
            optional_explicit = kwargs.get('optional', None)
            required_explicit = kwargs.get('required', None)
            if optional_explicit is not None and required_explicit is not None \
                    and required_explicit == optional_explicit:
                raise ThriftCLIError(
                    'Contradicting modifiers on required and optional for field - %s:%s %s' % (index, field_type, name))
            self.optional = (optional_explicit if optional_explicit is not None else True) and not required_explicit
            self.required = not self.optional and kwargs.get('required', True)
            self.modifier = 'required' if self.required else 'optional' if optional_explicit else ''

        def __eq__(self, other):
            return type(other) is type(self) and self.__dict__ == other.__dict__

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            modifier_str = ('%s ' % self.modifier) if self.modifier else ''
            default_str = (' = %s' % str(self.default)) if self.default is not None else ''
            str_params = (self.index, modifier_str, self.field_type, self.name, default_str)
            return '%s:%s%s %s%s' % str_params

    def __init__(self, reference, fields=None):
        """
        :param reference: a unique reference to the struct, defined as 'Namespace.name'.
        :param fields: a dictionary from field names to field objects that compromise the struct.
        """
        self.reference = reference
        self.fields = fields if fields is not None else {}

    def __eq__(self, other):
        return type(other) is type(self) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        sorted_fields = sorted(self.fields.values(), key=lambda field: field.index)
        return '%s ' % self.reference + ''.join(['\n\t%s' % str(field) for field in sorted_fields])
