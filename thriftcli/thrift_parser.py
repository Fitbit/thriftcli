import re
import os
import itertools

from .thrift_service import ThriftService
from .thrift_struct import ThriftStruct
from .thrift_cli_error import ThriftCLIError


class ThriftParser(object):
    """ Extracts struct, service, enum, and typedef definitions from thrift files.

    Call parse to extract definitions. The parser only knows about the last thrift file it parsed.
    Getters are provided to inspect the parse results.
    """

    INCLUDES_REGEX = re.compile(r'^include\s+\"(\w+.thrift)\"', flags=re.MULTILINE)
    STRUCTS_REGEX = re.compile(r'^([\r\t ]*?struct (\w+)[^}]+})', flags=re.MULTILINE)
    SERVICES_REGEX = re.compile(r'^([\r\t ]*?service (\w+)[^}]+})', flags=re.MULTILINE)
    ENUMS_REGEX = re.compile(r'^[\r\t ]*?enum (\w+)[^}]+}', flags=re.MULTILINE)
    ENDPOINTS_REGEX = re.compile(r'^[\r\t ]*(oneway)?\s*([^\n]*)\s+(\w+)\(([a-zA-Z0-9: ,.<>]*)\)',
                                 flags=re.MULTILINE)
    FIELDS_REGEX = re.compile(
        r'^[\r\t ]*(?:([\d+]):)?\s*(optional|required)?\s*([^\n=]+)?\s+(\w+)(?:\s*=\s*([^,;\s]+))?[,;\n]',
        flags=re.MULTILINE)
    TYPEDEFS_REGEX = re.compile(r'^[\r\t ]*typedef\s+([^\n]*)[\r\t ]+([^,;\n]*)', flags=re.MULTILINE)

    class Result(object):

        def __init__(self, structs=None, services=None, enums=None, typedefs=None):
            """ Container for results from parsing a thrift file.

            :param structs: Dictionary from struct reference to ThriftStruct object.
            :param services: Dictionary from service reference to ThriftService object.
            :param enums: Set of enum references.
            :param typedefs: Dictionary from typedef alias reference to unaliased field type.
            """
            self.structs = structs if structs is not None else {}
            self.services = services if services is not None else {}
            self.enums = enums if enums is not None else set([])
            self.typedefs = typedefs if typedefs is not None else {}

        def __eq__(self, other):
            return type(other) is type(self) and self.__dict__ == other.__dict__

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            return str({
                'structs': {name: str(struct) for name, struct in self.structs.items()},
                'services': {name: str(service) for name, service in self.services.items()},
                'enums': self.enums,
                'typedefs': self.typedefs
            })

        def merge_result(self, other):
            self.merge_structs(other.structs)
            self.merge_services(other.services)
            self.merge_enums(other.enums)
            self.merge_typedefs(other.typedefs)

        def merge_structs(self, structs):
            self.structs.update(structs)

        def merge_services(self, services):
            self.services.update(services)

        def merge_enums(self, enums):
            self.enums.update(enums)

        def merge_typedefs(self, typedefs):
            self.typedefs.update(typedefs)

    def __init__(self):
        self._thrift_path = None
        self._thrift_dir_paths = None
        self._thrift_content = None
        self._namespace = None
        self.result = None
        self._defined_references = None
        self._dependency_parsers = None

    def parse(self, thrift_path, thrift_dir_paths=None):
        """ Parses a thrift file into its structs, services, enums, and typedefs.

        :param thrift_path: The path to the thrift file being parsed.
        :type thrift_path: str
        :param thrift_dir_paths: Additional directories to search for when including thrift files.
        :type thrift_dir_paths: list of str
        :returns: Parse result object containing definitions of structs, services, enums, and typedefs.
        :rtype: ThriftParser.Result

        """
        if thrift_dir_paths is None:
            thrift_dir_paths = []
        self._thrift_path = thrift_path
        self._thrift_dir_paths = [os.path.dirname(thrift_path)] + thrift_dir_paths
        self._namespace = ThriftParser.get_package_name(thrift_path)
        self._thrift_content = self._load_file(thrift_path)
        self._dependency_parsers = self._parse_dependencies()
        self._defined_references = self.get_defined_references()
        self.result = ThriftParser.Result(
            self._parse_structs(), self._parse_services(), self._parse_enums(), self._parse_typedefs())
        for parser in self._dependency_parsers:
            self.result.merge_result(parser.result)
        return self.result

    @staticmethod
    def get_package_name(thrift_path):
        return thrift_path[:-len('.thrift')].split('/')[-1]

    @staticmethod
    def _load_file(path):
        with open(path, 'r') as file_to_read:
            return file_to_read.read()

    @staticmethod
    def _get_containing_directory(path):
        return path[:path.rindex('/')+1]

    def _parse_dependencies(self):
        names_to_include = set(ThriftParser.INCLUDES_REGEX.findall(self._thrift_content))
        names_found = set([])
        include_paths = []
        for thrift_dir_path, name in itertools.product(self._thrift_dir_paths, names_to_include):
            if name in names_found:
                continue
            path = os.path.join(thrift_dir_path, name)
            if os.path.isfile(path):
                include_paths.append(path)
                names_found.add(name)
        dependency_parsers = [ThriftParser() for _ in include_paths]
        for parser, path in zip(dependency_parsers, include_paths):
            parser.parse(path, self._thrift_dir_paths)
        return dependency_parsers

    def get_defined_references(self):
        struct_names = {name for _, name in ThriftParser.STRUCTS_REGEX.findall(self._thrift_content)}
        service_names = {name for _, name in ThriftParser.SERVICES_REGEX.findall(self._thrift_content)}
        enum_names = {name for name in ThriftParser.ENUMS_REGEX.findall(self._thrift_content)}
        typedef_names = {name for _, name in ThriftParser.TYPEDEFS_REGEX.findall(self._thrift_content)}
        names = struct_names | service_names | enum_names | typedef_names
        dependency_references = set([])
        for parser in self._dependency_parsers:
            dependency_references = dependency_references | parser.get_defined_references()
        references = {'%s.%s' % (self._namespace, name) for name in names} | dependency_references
        return references

    def _parse_structs(self):
        definitions_by_reference = self._parse_struct_definitions()
        fields_by_reference = {reference: self._parse_fields_from_struct_definition(definition)
                               for reference, definition in definitions_by_reference.items()}
        structs = {reference: ThriftStruct(reference, fields) for reference, fields in fields_by_reference.items()}
        return structs

    def _parse_struct_definitions(self):
        structs_list = ThriftParser.STRUCTS_REGEX.findall(self._thrift_content)
        structs = {'%s.%s' % (self._namespace, name): definition for definition, name in structs_list}
        return structs

    def _parse_fields_from_struct_definition(self, definition):
        field_matches = ThriftParser.FIELDS_REGEX.findall(definition)
        fields = [self._construct_field_from_field_match(field_match) for field_match in field_matches]
        self._assign_field_indices(fields)
        fields = {field.name: field for field in fields}
        return fields

    def _parse_services(self):
        definitions_by_reference = self._parse_service_definitions()
        endpoints_by_reference = {reference: self._parse_endpoints_from_service_definition(definition)
                                  for reference, definition in definitions_by_reference.items()}
        services = {reference: ThriftService(reference, endpoints)
                    for reference, endpoints in endpoints_by_reference.items()}
        return services

    def _parse_service_definitions(self):
        services_list = ThriftParser.SERVICES_REGEX.findall(self._thrift_content)
        services = {'%s.%s' % (self._namespace, name): definition for definition, name in services_list}
        return services

    def _parse_endpoints_from_service_definition(self, definition):
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
        field_strings = self._split_fields_string(fields_string)
        field_matches = [ThriftParser.FIELDS_REGEX.findall(field_string + '\n') for field_string in field_strings]
        field_matches = [field_match[0] for field_match in field_matches if len(field_match)]
        fields = [self._construct_field_from_field_match(field_match) for field_match in field_matches]
        self._assign_field_indices(fields)
        return fields

    @staticmethod
    def _assign_field_indices(fields):
        last_index = 0
        for field in fields:
            if not field.index or field.index <= last_index:
                field.index = last_index + 1
            last_index = field.index

    @staticmethod
    def _split_fields_string(fields_string):
        field_strings = []
        bracket_depth = 0
        last_index = 0
        for i, char in enumerate(fields_string):
            if char == '<':
                bracket_depth += 1
            elif char == '>':
                bracket_depth -= 1
            elif char == ',' and bracket_depth == 0:
                field_string = fields_string[last_index:i].strip()
                field_strings.append(field_string)
                last_index = i + 1
        field_string = fields_string[last_index:].strip()
        field_strings.append(field_string)
        return field_strings

    def _parse_enums(self):
        enums_list = ThriftParser.ENUMS_REGEX.findall(self._thrift_content)
        enums = {'%s.%s' % (self._namespace, enum) for enum in enums_list}
        return enums

    def _parse_typedefs(self):
        typedef_matches = ThriftParser.TYPEDEFS_REGEX.findall(self._thrift_content)
        typedefs = {'%s.%s' % (self._namespace, alias): self._apply_namespace(field_type)
                    for (field_type, alias) in typedef_matches}
        return typedefs

    def _apply_namespace(self, field_type):
        ns_field_type = '%s.%s' % (self._namespace, field_type)
        if ns_field_type in self._defined_references:
            return ns_field_type
        elif field_type.startswith('list<'):
            elem_type = field_type[field_type.index('<') + 1:field_type.rindex('>')]
            return 'list<%s>' % self._apply_namespace(elem_type)
        elif field_type.startswith('set<'):
            elem_type = field_type[field_type.index('<') + 1:field_type.rindex('>')]
            return 'set<%s>' % self._apply_namespace(elem_type)
        elif field_type.startswith('map<'):
            return self._apply_map_namespace(field_type)
        return field_type

    def _apply_map_namespace(self, field_type):
        types_string = field_type[field_type.index('<') + 1:field_type.rindex('>')]
        split_index = ThriftParser.calc_map_types_split_index(types_string)
        if split_index == -1:
            raise ThriftCLIError('Invalid type formatting for map - \'%s\'' % types_string)
        key_type = types_string[:split_index].strip()
        elem_type = types_string[split_index + 1:].strip()
        return 'map<%s, %s>' % (self._apply_namespace(key_type), self._apply_namespace(elem_type))

    def _construct_field_from_field_match(self, field_match):
        (index, modifier, field_type, name, default) = field_match
        field_type = self._apply_namespace(field_type)
        required = True if modifier == 'required' else None
        optional = True if modifier == 'optional' else None
        default = default if len(default) else None
        return ThriftStruct.Field(index, field_type, name, required=required, optional=optional, default=default)

    @staticmethod
    def calc_map_types_split_index(types_string):
        """ Returns the index of the comma separating the key and value types in a map type.

        :param types_string:
        :return: index of top-level separating comma
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

    def get_fields_for_endpoint(self, service_reference, method_name):
        """ Returns all argument fields declared for a given endpoint.

        :param service_reference: The reference ('package.Service') of the service declaring the endpoint.
        :type service_reference: str
        :param method_name: The name of the method representing the endpoint.
        :type method_name: str
        :returns: Fields that are declared as arguments for the provided endpoint.
        :rtype: list of ThriftStruct.Field
        :raises: KeyError, AttributeError

        """
        return self.result.services[service_reference].endpoints[method_name].fields

    def get_fields_for_struct_name(self, struct_name):
        """ Returns all fields that compromise the given struct.

        :param struct_name: The name of the struct.
        :type struct_name: str
        :returns: Fields that are declared as components for the provided struct.
        :rtype: list of ThriftStruct.Field
        :raises: KeyError, AttributeError

        """
        return self.result.structs[struct_name].fields

    def has_struct(self, struct_name):
        """ Checks if the given struct was found in the last parse.

        :param struct_name: The name of the struct to check for.
        :type struct_name: str
        :returns: True if the struct was declared in the last parsed thrift file. False otherwise.
        :rtype: bool

        """
        if not self.result:
            return False
        return struct_name in self.result.structs

    def has_enum(self, enum_name):
        """ Checks if the given enum was found in the last parse.

        :param enum_name: The name of the enum to check for.
        :type enum_name: str
        :returns: True if the enum was declared in the last parsed thrift file. False otherwise.
        :rtype: bool

        """
        if not self.result:
            return False
        return enum_name in self.result.enums

    def has_typedef(self, alias):
        """ Checks if there was a typedef for the given alias found in the last parse.

        :param alias: The alias of the typedef to check for.
        :type alias: str
        :returns: True if a typedef was declared for the alias in the last parsed thrift file. False otherwise.
        :rtype: bool

        """
        if not self.result:
            return False
        return alias in self.result.typedefs

    def get_typedef(self, alias):
        """ Returns the thrift type for the given alias according to the typedefs found in the last parse.

        :param alias: The alias of the typedef to check for.
        :type alias: str
        :returns: The thrift type for the given alias according to the typedefs in the last parsed thrift file.
        :raises: KeyError

        """
        if not self.result:
            return False
        return self.result.typedefs[alias]

    def unalias_type(self, field_type):
        """ Returns the unaliased thrift type according to the typedefs found in the last parse.

        :param field_type: The potentially aliased thrift type.
        :type field_type: str
        :returns: The unaliased thrift type according to the typedefs in the last parsed thrift file.
        :raises: ThriftCLIError

        """
        type_set = {field_type}
        while self.has_typedef(field_type):
            field_type = self.get_typedef(field_type)
            if field_type in type_set:
                raise ThriftCLIError('Circular typedef dependency involving \'%s\'' % field_type)
            type_set.add(field_type)
        return field_type
