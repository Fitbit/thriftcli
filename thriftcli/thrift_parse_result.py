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


class ThriftParseResult(object):
    """ Contains all necessary definitions and declarations extracted from parsing a Thrift file.

    A ThriftParseResult holds:
    1. A map of struct names to ThriftStructs
    2. A map of service names to ThriftServices
    3. A set of all enum type names
    4. A map of initial types to aliased types, defined by typedefs
    5. A map from file basenames to python namespaces

    A ThriftParseResult includes all definitions from the parsed Thrift file as well as its dependencies.

    """
    def __init__(self, structs=None, services=None, enums=None, typedefs=None, namespaces=None):
        """ Container for results from parsing a thrift file.

        :param structs: dictionary from struct reference to ThriftStruct object.
        :param services: dictionary from service reference to ThriftService object.
        :param enums: set of enum references.
        :param typedefs: dictionary from typedef alias reference to unaliased field type.
        :param typedefs: dictionary from file basenames to python namespaces.

        """
        self.structs = structs if structs is not None else {}
        self.services = services if services is not None else {}
        self.enums = enums if enums is not None else set([])
        self.typedefs = typedefs if typedefs is not None else {}
        self.namespaces = namespaces if namespaces is not None else {}

    def __eq__(self, other):
        return type(other) is type(self) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str({
            'structs': {name: str(struct) for name, struct in self.structs.items()},
            'services': {name: str(service) for name, service in self.services.items()},
            'enums': self.enums,
            'typedefs': self.typedefs,
            'namespaces': self.namespaces
        })

    def merge_result(self, other):
        """ Add the definitions from another ThriftParseResult into this one.

        :param other: another ThriftParseResult to merge into self.

        """
        self.merge_structs(other.structs)
        self.merge_services(other.services)
        self.merge_enums(other.enums)
        self.merge_typedefs(other.typedefs)
        self.merge_namespaces(other.namespaces)

    def merge_structs(self, structs):
        """ Add the structs from another ThriftParseResult into this one.

        :param structs: a map of struct names to ThriftStructs to be added to self's structs.

        """
        self.structs.update(structs)

    def merge_services(self, services):
        """ Add the services from another ThriftParseResult into this one.

        :param services: a map of service names to ThriftServices to be added to self's services.

        """
        self.services.update(services)

    def merge_enums(self, enums):
        """ Add the enums from another ThriftParseResult into this one.

        :param enums: a set of enum type names to be added to self's enums.

        """
        self.enums.update(enums)

    def merge_typedefs(self, typedefs):
        """ Add the typedefs from another ThriftParseResult into this one.

        :param typedefs: a map of initial types to aliased types to be added to self's typedefs.

        """
        self.typedefs.update(typedefs)

    def merge_namespaces(self, namespaces):
        """ Add the namespaces from another ThriftParseResult into this one.
        """
        self.namespaces.update(namespaces)

    def get_fields_for_endpoint(self, service_reference, method_name):
        """ Returns all argument fields declared for a given endpoint.
    
        :param service_reference: the reference ('package.Service') of the service declaring the endpoint.
        :type service_reference: str
        :param method_name: the name of the method representing the endpoint.
        :type method_name: str
        :returns: fields that are declared as arguments for the provided endpoint.
        :rtype: list of ThriftStruct.Field
        :raises: KeyError, AttributeError
    
        """
        return self.services[service_reference].endpoints[method_name].fields

    def get_fields_for_struct_name(self, struct_name):
        """ Returns all fields that compromise the given struct.
    
        :param struct_name: the name of the struct.
        :type struct_name: str
        :returns: fields that are declared as components for the provided struct.
        :rtype: list of ThriftStruct.Field
        :raises: KeyError, AttributeError
    
        """
        return self.structs[struct_name].fields

    def has_enum(self, enum_name):
        """ Checks if the given enum was found in the last parse.
    
        :param enum_name: the name of the enum to check for.
        :type enum_name: str
        :returns: True if the enum was declared in the last parsed thrift file. False otherwise.
        :rtype: bool
    
        """
        if not self:
            return False
        return enum_name in self.enums

    def get_struct(self, struct_name):
        """ Returns the struct for the given struct name.
    
        :param struct_name: the name of the struct to look up.
        :type struct_name: str
        :returns: the associated ThriftStruct or None.
        :rtype: ThriftStruct or None
    
        """
        if not self or struct_name not in self.structs:
            return None
        return self.structs[struct_name]

    def get_typedef(self, alias):
        """ Returns the type for the given alias according to the typedefs found in the last parse.
    
        :param alias: the alias of the typedef to check for.
        :type alias: str
        :returns: the type for the given alias according to the typedefs in the last parsed thrift file.
        :rtype: str or None
    
        """
        if not self or alias not in self.typedefs:
            return None
        return self.typedefs[alias]

    def unalias_type(self, field_type):
        """ Returns the unaliased type according to the typedefs found in the last parse.
    
        :param field_type: the potentially aliased type.
        :type field_type: str
        :returns: the unaliased type according to the typedefs in the last parsed thrift file.
        :raises: ThriftCLIError
    
        """
        type_set = {field_type}
        while self.get_typedef(field_type) is not None:
            field_type = self.get_typedef(field_type)
            if field_type in type_set:
                raise ThriftCLIError('Circular typedef dependency involving \'%s\'' % field_type)
            type_set.add(field_type)
        return field_type
