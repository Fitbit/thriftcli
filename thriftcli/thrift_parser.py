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

import itertools
import os
import re

from .thrift_cli_error import ThriftCLIError
from .thrift_parse_result import ThriftParseResult
from .thrift_service import ThriftService
from .thrift_struct import ThriftStruct


class ThriftParser(object):
    """ Extracts struct, service, enum, and typedef definitions from thrift files.

    Call parse to extract a ThriftParseResult object.

    The parser works by taking the following steps:
    1. Parse all dependencies and inherit their results
    2. Match file content with regexs and consolidate the following in a ThriftParseResult:
        - Struct definitions as ThriftStructs
        - Service definitions as ThriftServices
        - Enum declarations as Enum type names (the names/values aren't needed)
        - Typedefs as mappings from initial type to aliased type
    3. Merge the ThriftParseResults from the dependencies into the ThriftParseResult from step 2
    4. Return the merged ThriftParseResult

    """

    # Matches Thrift includes statements. Captures the dependency file names.
    #
    # For example:
    #   includes "File.thrift"
    #   => ("File.thrift")
    INCLUDES_REGEX = re.compile(r'^include\s+\"([\w./]+.thrift)\"', flags=re.MULTILINE)

    # Matches Thrift python namespace statements. Captures the namespace.
    #
    # For example:
    #   namespace py com.example.thrift.thriftpy
    #   => ("com.example.thrift.thriftpy")
    NAMESPACE_PY_REGEX = re.compile(r'^namespace\s+py\s+(\S+)', flags=re.MULTILINE)

    # Matches struct definitions. Captures the whole definition and the struct name.
    #
    # For example:
    #   struct MyStruct {
    #       1:required i64 myNum = 0
    #   }
    #   => ("struct MyStruct {\n1:required i64 myNum = 0\n}",
    #       "MyStruct")
    STRUCTS_REGEX = re.compile(r'^([\r\t ]*?struct (\w+)[^}]+})', flags=re.MULTILINE)

    # Matches service definitions. Captures the whole definition, the service name, and optionally the extended service.
    #
    # For example:
    #   service MyService extends MyOtherService {
    #       i64 add(1:i64 num1, 2:i64 num2)
    #   }
    #   => ("service MyService extends MyOtherService {\ni64 add(1:i64 num1, 2:i64 num2)\n}",
    #       "MyService",
    #       "MyOtherService")
    SERVICES_REGEX = re.compile(r'^([\r\t ]*?service\s+(\w+)(?:\s+extends\s+([\w.]+))?[^}]+})', flags=re.MULTILINE)

    # Matches enum definitions. Captures the enum name.
    #
    # For example:
    #   enum MyEnum {
    #       ONE = 0x64,
    #       TWO = 2,
    #       THREE
    #   }
    #   => ("MyEnum")
    ENUMS_REGEX = re.compile(r'^[\r\t ]*?enum (\w+)[^}]+}', flags=re.MULTILINE)

    # Matches endpoint declarations. Captures oneway, the return type, the endpoint name, and the fields string.
    #
    # For example:
    #   i64 add(1:i64 num1, 2:i64 num2)
    #   => ("",
    #       "i64",
    #       "add",
    #       "1:i64 num1, 2:i64 num2")
    ENDPOINTS_REGEX = re.compile(r'^[\r\t ]*(oneway)?\s*([^\n]*)\s+(\w+)\(([a-zA-Z0-9: ,.<>]*)\)',
                                 flags=re.MULTILINE)

    # Matches field declarations. Captures index, optional/required, field type, field name, and default value.
    #
    # Note that only "field type and field name" are necessary. The other parts are optional.
    #
    # For example:
    #   1:required i64 myNum = 0
    #   => ("1",
    #       "required",
    #       "i64",
    #       "myNum",
    #       "0")
    #   11: optional set<Cohort> cohorts
    #   => ("11",
    #       "optional",
    #       "set<Cohort>",
    #       "cohorts",
    #       "")
    #   string thing_one
    #   => ("",
    #       "required",
    #       "string",
    #       "thing_one",
    #       "")
    FIELDS_REGEX = re.compile(
        r'^[\r\t ]*(\d+\s*:)?\s*(optional|required)?\s*([^\n=]+)?\s+(\w+)(?:\s*=\s*([^,;\s]+))?[,;\n]',
        flags=re.MULTILINE)

    # Matches typedefs. Captures initial type name and aliased type name.
    #
    # For example:
    #   typedef MyNumber i64
    #   => ("MyNumber",
    #       "i64")
    TYPEDEFS_REGEX = re.compile(r'^[\r\t ]*typedef\s+([^\n]*)[\r\t ]+([^,;\n]*)', flags=re.MULTILINE)

    def __init__(self, thrift_path, thrift_dir_paths=None):
        """

        :param thrift_path: the path to the thrift file being parsed.
        :type thrift_path: str
        :param thrift_dir_paths: additional directories to search for when including thrift files.
        :type thrift_dir_paths: list of str

        """
        if thrift_dir_paths is None:
            thrift_dir_paths = []
        self._thrift_path = thrift_path
        self._thrift_dir_paths = [os.path.dirname(thrift_path)] + thrift_dir_paths
        self._namespace = ThriftParser.get_package_name(thrift_path)
        self._thrift_content = self._load_file(self._thrift_path)
        self._references = set([])
        self._result = None

    def parse(self):
        """ Parses a thrift file into its structs, services, enums, typedefs, and namespaces.

        :returns: parse result object containing definitions of structs, services, enums, typedefs, and namespaces.
        :rtype: ThriftParseResult

        """
        self._result = ThriftParseResult()
        for path in self._get_dependency_paths():
            parser = ThriftParser(path, self._thrift_dir_paths)
            self._references.update(parser._parse_references())
            self._result.merge_result(parser.parse())
        self._references.update(self._parse_references())
        parse_result = ThriftParseResult(
            self._parse_structs(), self._parse_services(), self._parse_enums(), self._parse_typedefs(),
            self._parse_namespace_py())
        self._result.merge_result(parse_result)
        return self._result

    @staticmethod
    def get_package_name(thrift_path):
        """ Returns the name of the package generated by a thrift file.

        :param thrift_path: the path to the thrift file used for generation
        :type thrift_path: str
        :returns: the name of the generated package
        :rtype: str

        """
        return os.path.splitext(os.path.basename(thrift_path))[0]

    @staticmethod
    def _load_file(path):
        """ Returns the contents of a file.

        :param path: the path of the file to load
        :type path: str
        :returns: the content of the file
        :rtype: str

        """
        with open(path, 'r') as file_to_read:
            return file_to_read.read()

    def _get_dependency_paths(self):
        """ Returns the paths to all of the parsed thrift file's dependencies.

        :returns: the paths to all of the parsed thrift file's dependencies, which are denoted by includes statements
        :rtype: list of str

        """
        names_to_include = set(ThriftParser.INCLUDES_REGEX.findall(self._thrift_content))
        names_found = set([])
        dependency_paths = []
        for thrift_dir_path, name in itertools.product(self._thrift_dir_paths, names_to_include):
            if name in names_found:
                continue
            path = os.path.join(thrift_dir_path, name)
            if os.path.isfile(path):
                dependency_paths.append(path)
                names_found.add(name)
        return dependency_paths

    def _parse_namespace_py(self):
        basename = ThriftParser.get_package_name(self._thrift_path)
        namespace_list = ThriftParser.NAMESPACE_PY_REGEX.findall(self._thrift_content)
        if namespace_list:
            return {basename: namespace_list[0]}
        else:
            return {basename: basename}

    def _parse_references(self):
        """ Returns the set of references defined by the parsed thrift file.

        A reference is a struct, service, enum, or typedef name prepended with the defining thrift file name.

        For example: MyStruct defined in MyThrift.thrift has a reference of MyThrift.MyStruct

        :returns: the set of references defined by the parsed thrift file
        :rtype: set of str

        """
        struct_names = {name for _, name in ThriftParser.STRUCTS_REGEX.findall(self._thrift_content)}
        service_names = {name for _, name, _ in ThriftParser.SERVICES_REGEX.findall(self._thrift_content)}
        enum_names = {name for name in ThriftParser.ENUMS_REGEX.findall(self._thrift_content)}
        typedef_names = {name for _, name in ThriftParser.TYPEDEFS_REGEX.findall(self._thrift_content)}
        names = struct_names | service_names | enum_names | typedef_names
        references = {'%s.%s' % (self._namespace, name) for name in names}
        return references

    def _parse_structs(self):
        """ Returns the structs defined by the parsed thrift file, keyed by reference.

        :returns: a dict of struct references to ThriftStructs for each struct defined in the parsed thrift file
        :rtype: dict of str to ThriftStruct

        """
        definitions_by_reference = self._parse_struct_definitions()
        fields_by_reference = {reference: self._parse_fields_from_struct_definition(definition)
                               for reference, definition in definitions_by_reference.items()}
        structs = {reference: ThriftStruct(reference, fields) for reference, fields in fields_by_reference.items()}
        return structs

    def _parse_struct_definitions(self):
        """ Returns the struct definitions found in the parsed thrift file, keyed by reference.

        :returns: a dict of struct references to struct definitions for each struct defined in the parsed thrift file
        :rtype: dict of str to str

        """
        structs_list = ThriftParser.STRUCTS_REGEX.findall(self._thrift_content)
        structs = {'%s.%s' % (self._namespace, name): definition for definition, name in structs_list}
        return structs

    def _parse_fields_from_struct_definition(self, definition):
        """ Returns the fields in the struct definition, keyed by field name.

        :returns: a dict of field names to ThriftStruct.Fields for each field defined in a struct definition
        :rtype: dict of str to ThriftStruct.Field

        """
        field_matches = ThriftParser.FIELDS_REGEX.findall(definition)
        fields = [self._construct_field_from_field_match(field_match) for field_match in field_matches]
        self._assign_field_indices(fields)
        fields = {field.name: field for field in fields}
        return fields

    def _parse_services(self):
        """ Returns the services defined by the parsed thrift file, keyed by reference.

        :returns: a dict of service references to ThriftServices for each service defined in the parsed thrift file
        :rtype: dict of str to ThriftService

        """
        definitions_by_reference = self._parse_service_definitions()
        known_services = self._result.services
        services = known_services.copy()
        for reference, (definition, extends) in definitions_by_reference:
            endpoints = self._build_service_endpoints(services, definition, extends)
            service = ThriftService(reference, endpoints, extends)
            services[reference] = service
        return services

    def _parse_service_definitions(self):
        """ Returns the service definitions found in the parsed thrift file, keyed by reference.

        :returns: a dict of service references to service definitions for each service defined in the parsed thrift file
        :rtype: dict of str to str

        """
        services_list = ThriftParser.SERVICES_REGEX.findall(self._thrift_content)
        services = [(self._apply_namespace(name), (definition, self._apply_namespace(extends) if extends else None))
                    for definition, name, extends in services_list]
        return services

    def _build_service_endpoints(self, services, definition, extends=None):
        """ Returns the ThriftService.Endpoints contained by a service definition, including from service inheritance

        :param services: a dict of service references to ThriftServices that have been parsed so far
        :type services: dict of str to ThriftService
        :param definition: the service definition that endpoints are being built for
        :type definition: str
        :param extends: a reference to the service being extended, or None
        :type extends: str or None
        :return: a dict of endpoint names to ThriftService.Endpoints provided by the given service definition
        :rtype: dict of str to ThriftService.Endpoint

        """
        endpoints = services[extends].endpoints.copy() if extends is not None else {}
        parsed_endpoints = self._parse_endpoints_from_service_definition(definition)
        endpoints.update(parsed_endpoints)
        return endpoints

    def _parse_endpoints_from_service_definition(self, definition):
        """ Returns the endpoints in the service definition, keyed by method name.

        :param definition: the service definition to parse
        :type definition: str
        :returns: a dict of endpoint names to ThriftService.Endpoints provided by the given service definition
        :rtype: dict of str to ThriftService.Endpoint

        """
        endpoint_matches = ThriftParser.ENDPOINTS_REGEX.findall(definition)
        (oneways, return_types, names, fields_strings) = zip(*endpoint_matches)
        (oneways, return_types, names, fields_strings) = \
            (list(oneways), list(return_types), list(names), list(fields_strings))
        return_types = [self._apply_namespace(return_type) for return_type in return_types]
        fields_lists = [self._parse_fields_from_fields_string(fields_string) for fields_string in fields_strings]
        fields_dicts = [{field.name: field for field in field_list} for field_list in fields_lists]
        endpoints = [ThriftService.Endpoint(return_type, name, fields, oneway=oneway) for
                     oneway, return_type, name, fields in zip(oneways, return_types, names, fields_dicts)]
        endpoints = {endpoint.name: endpoint for endpoint in endpoints}
        return endpoints

    def _parse_fields_from_fields_string(self, fields_string):
        """ Returns the fields in the field string.

        :param fields_string: the field string to parse
        :type fields_string: str
        :returns: a list of ThriftStruct.Fields defined by the field string
        :rtype: list of ThriftStruct.Field

        """
        field_strings = self.split_fields_string(fields_string)
        field_matches = [ThriftParser.FIELDS_REGEX.findall(field_string + '\n') for field_string in field_strings]
        field_matches = [field_match[0] for field_match in field_matches if len(field_match)]
        fields = [self._construct_field_from_field_match(field_match) for field_match in field_matches]
        self._assign_field_indices(fields)
        return fields

    def _parse_enums(self):
        """ Returns the set of enum references defined by the parsed thrift file.

        :returns: the set of enum references defined by the parsed thrift file
        :rtype: set of str

        """
        enums_list = ThriftParser.ENUMS_REGEX.findall(self._thrift_content)
        enums = {'%s.%s' % (self._namespace, enum) for enum in enums_list}
        return enums

    def _parse_typedefs(self):
        """ Returns the typedefs defined by the parsed thrift file, keyed by alias.

        :returns: a dict of aliased types to unaliased types
        :rtype: dict of str to str

        """
        typedef_matches = ThriftParser.TYPEDEFS_REGEX.findall(self._thrift_content)
        typedefs = {self._apply_namespace(alias): self._apply_namespace(field_type)
                    for (field_type, alias) in typedef_matches}
        return typedefs

    def _apply_namespace(self, field_type):
        """ Applies the package namespace to the field type appropriately.

        For example: Given MyStruct defined in MyThrift, "list<MyStruct>" => "list<MyThrift.MyStruct>"

        :param field_type: the type of the field to namespace
        :type field_type: str
        :returns: the namespaced field type
        :rtype: str

        """
        if field_type is None:
            return None
        ns_field_type = '%s.%s' % (self._namespace, field_type)
        if ns_field_type in self._references:
            return ns_field_type
        elif field_type.startswith('list<'):
            elem_type = field_type[field_type.index('<') + 1:field_type.rindex('>')]
            return 'list<%s>' % self._apply_namespace(elem_type)
        elif field_type.startswith('set<'):
            elem_type = field_type[field_type.index('<') + 1:field_type.rindex('>')]
            return 'set<%s>' % self._apply_namespace(elem_type)
        elif field_type.startswith('map<'):
            return self._apply_namespace_to_map(field_type)
        return field_type

    def _apply_namespace_to_map(self, field_type):
        """ Applies the package namespace to the map's key and value types appropriately.

        For example: Given MyStruct defined in MyThrift, "map<i64, MyStruct>" => "map<i64, MyThrift.MyStruct>"

        :param field_type: the type of the field to namespace, fitting the format of map<TYPE1, TYPE2>
        :type field_type: str
        :returns: the namespaced field type
        :rtype: str

        """
        types_string = field_type[field_type.index('<') + 1:field_type.rindex('>')]
        split_index = ThriftParser.calc_map_types_split_index(types_string)
        if split_index == -1:
            raise ThriftCLIError('Invalid type formatting for map - \'%s\'' % types_string)
        key_type = types_string[:split_index].strip()
        elem_type = types_string[split_index + 1:].strip()
        return 'map<%s, %s>' % (self._apply_namespace(key_type), self._apply_namespace(elem_type))

    def _construct_field_from_field_match(self, field_match):
        """ Construct a ThriftStruct.Field from a regex match on a field declaration.

        :param field_match: a tuple of captured groups from the FIELDS_REGEX
        :type field_match: tuple of (str, str, str, str, str)
        :returns: a ThriftStruct.Field represented by the groups captured in the field declaration
        :rtype: ThriftStruct.Field

        """
        (index, modifier, field_type, name, default) = field_match
        field_type = self._apply_namespace(field_type)
        required = True if modifier == 'required' else None
        optional = True if modifier == 'optional' else None
        default = default if len(default) else None
        return ThriftStruct.Field(index, field_type, name, required=required, optional=optional, default=default)

    @staticmethod
    def _assign_field_indices(fields):
        """ Assign indices to a list of fields to match thrift.

        :param fields: a list of ThriftStruct.Fields to assign indices to
        :type fields: list of ThriftStruct.Field

        """
        last_index = 0
        for field in fields:
            if not field.index or field.index <= last_index:
                field.index = last_index + 1
            last_index = field.index

    @staticmethod
    def split_fields_string(fields_string, opening='<', closing='>', delim=','):
        """ Split a fields string into a list of field declarations.

        :param fields_string: the string containing multiple field declarations.
        :type fields_string: str
        :param opening: a string containing all characters that are considered opening brackets
        :type opening: str
        :param closing: a string containing all characters that are considered closing brackets
        :type closing: str
        :param delim: a string containing all characters that are considered delimiters
        :type delim: str
        :returns: list of field declarations.
        :rtype: list of str

        """
        field_strings = []
        bracket_depth = 0
        last_index = 0
        for i, char in enumerate(fields_string):
            if char in opening:
                bracket_depth += 1
            elif char in closing:
                bracket_depth -= 1
            elif char in delim and bracket_depth == 0:
                field_string = fields_string[last_index:i].strip()
                field_strings.append(field_string)
                last_index = i + 1
        field_string = fields_string[last_index:].strip()
        field_strings.append(field_string)
        return field_strings

    @staticmethod
    def calc_map_types_split_index(types_string):
        """ Returns the index of the comma separating the key and value types in a map type.

        :param types_string: the string declaring the map's type.
        :returns: index of top-level separating comma
        :rtype: int

        """
        bracket_depth = 0
        for i, char in enumerate(types_string):
            if char == '<':
                bracket_depth += 1
            elif char == '>':
                bracket_depth -= 1
            elif char == ',' and bracket_depth == 0:
                return i
        return -1
