import re

from .thrift_service import ThriftService
from .thrift_struct import ThriftStruct
import thrift_cli


class ThriftParser(object):
    """ Extracts struct, service, enum, and typedef definitions from thrift files.

    Call parse to extract definitions. The parser only knows about the last thrift file it parsed.
    Getters are provided to inspect the parse results.
    """

    class Result(object):
        def __init__(self, structs, services, enums, typedefs):
            self.structs = structs
            self.services = services
            self.enums = enums
            self.typedefs = typedefs

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

    def __init__(self):
        self._thrift_path = None
        self._thrift_content = None
        self._result = None
        self._structs_regex = re.compile(r'^([\r\t ]*?struct (\w+)[^}]+})', flags=re.MULTILINE)
        self._services_regex = re.compile(r'^([\r\t ]*?service (\w+)[^}]+})', flags=re.MULTILINE)
        self._enums_regex = re.compile(r'^[\r\t ]*?enum (\w+)[^}]+}', flags=re.MULTILINE)
        self._endpoints_regex = re.compile(r'^[\r\t ]*(oneway)?\s*([^\n]*)\s+(\w+)\(([a-zA-Z0-9: ,<>]*)\)',
                                           flags=re.MULTILINE)
        self._fields_regex = re.compile(
            r'^[\r\t ]*(?:([\d+]):)?\s*(optional|required)?\s*([^\n=]+)?\s+(\w+)(?:\s*=\s*([^,;\s]+))?[,;\n]',
            flags=re.MULTILINE)
        self._typedefs_regex = re.compile(r'^[\r\t ]*typedef\s+([^\n]*)[\r\t ]+([^,;\n]*)', flags=re.MULTILINE)

    def parse(self, thrift_path):
        """ Parses a thrift file into its structs, services, enums, and typedefs.

        :param thrift_path: The path to the thrift file being parsed.
        :type thrift_path: str
        :returns: Parse result object containing definitions of structs, services, enums, and typedefs.
        :rtype: ThriftParser.Result

        """
        self._thrift_path = thrift_path
        self._thrift_content = self._load_file(thrift_path)
        self._result = ThriftParser.Result(
            self._parse_structs(), self._parse_services(), self._parse_enums(), self._parse_typedefs())
        return self._result

    @staticmethod
    def _load_file(path):
        with open(path, 'r') as file_to_read:
            return file_to_read.read()

    def _parse_structs(self):
        definitions_by_name = self._parse_struct_definitions()
        fields_by_name = {name: self._parse_fields_from_struct_definition(definition) for name, definition in
                          definitions_by_name.items()}
        structs = {name: ThriftStruct(name, fields) for name, fields in fields_by_name.items()}
        return structs

    def _parse_struct_definitions(self):
        structs_list = self._structs_regex.findall(self._thrift_content)
        structs = {name: definition for (definition, name) in structs_list}
        return structs

    def _parse_fields_from_struct_definition(self, definition):
        field_matches = self._fields_regex.findall(definition)
        fields = [self._construct_field_from_field_match(field_match) for field_match in field_matches]
        self._assign_field_indices(fields)
        fields = {field.name: field for field in fields}
        return fields

    def _parse_services(self):
        definitions_by_name = self._parse_service_definitions()
        endpoints_by_name = {name: self._parse_endpoints_from_service_definition(definition) for name, definition in
                             definitions_by_name.items()}
        services = {name: ThriftService(name, endpoints) for name, endpoints in endpoints_by_name.items()}
        return services

    def _parse_service_definitions(self):
        services_list = self._services_regex.findall(self._thrift_content)
        services = {name: definition for (definition, name) in services_list}
        return services

    def _parse_endpoints_from_service_definition(self, definition):
        endpoint_matches = self._endpoints_regex.findall(definition)
        (oneways, return_types, names, fields_strings) = zip(*endpoint_matches)
        (oneways, return_types, names, fields_strings) = \
            (list(oneways), list(return_types), list(names), list(fields_strings))
        fields_lists = [self._parse_fields_from_fields_string(fields_string) for fields_string in fields_strings]
        fields_dicts = [{field.name: field for field in field_list} for field_list in fields_lists]
        endpoints = [ThriftService.Endpoint(return_type, name, fields, oneway=oneway) for
                     oneway, return_type, name, fields in zip(oneways, return_types, names, fields_dicts)]
        endpoints = {endpoint.name: endpoint for endpoint in endpoints}
        return endpoints

    def _parse_fields_from_fields_string(self, fields_string):
        field_strings = self._split_fields_string(fields_string)
        field_matches = [self._fields_regex.findall(field_string + '\n') for field_string in field_strings]
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
        enums_list = self._enums_regex.findall(self._thrift_content)
        enums = set(enums_list)
        return enums

    def _parse_typedefs(self):
        typedef_matches = self._typedefs_regex.findall(self._thrift_content)
        typedef_dict = {alias: field_type for field_type, alias in typedef_matches}
        return typedef_dict

    @staticmethod
    def _construct_field_from_field_match(field_match):
        (index, modifier, field_type, name, default) = field_match
        required = True if modifier == 'required' else None
        optional = True if modifier == 'optional' else None
        default = default if len(default) else None
        return ThriftStruct.Field(index, field_type, name, required=required, optional=optional, default=default)

    def get_fields_for_endpoint(self, service_name, method_name):
        """ Returns all argument fields declared for a given endpoint.

        :param service_name: The name of the service declaring the endpoint.
        :type service_name: str
        :param method_name: The name of the method representing the endpoint.
        :type method_name: str
        :returns: Fields that are declared as arguments for the provided endpoint.
        :rtype: list of ThriftStruct.Field
        :raises: KeyError

        """
        return self._result.services[service_name].endpoints[method_name].fields

    def get_fields_for_struct_name(self, struct_name):
        """ Returns all fields that compromise the given struct.

        :param struct_name: The name of the struct.
        :type struct_name: str
        :returns: Fields that are declared as components for the provided struct.
        :rtype: list of ThriftStruct.Field
        :raises: KeyError

        """
        return self._result.structs[struct_name].fields

    def has_struct(self, struct_name):
        """ Checks if the given struct was found in the last parse.

        :param struct_name: The name of the struct to check for.
        :type struct_name: str
        :returns: True if the struct was declared in the last parsed thrift file. False otherwise.
        :rtype: bool

        """
        return struct_name in self._result.structs

    def has_enum(self, enum_name):
        """ Checks if the given enum was found in the last parse.

        :param enum_name: The name of the enum to check for.
        :type enum_name: str
        :returns: True if the enum was declared in the last parsed thrift file. False otherwise.
        :rtype: bool

        """
        return enum_name in self._result.enums

    def has_typedef(self, alias):
        """ Checks if there was a typedef for the given alias found in the last parse.

        :param alias: The alias of the typedef to check for.
        :type alias: str
        :returns: True if a typedef was declared for the alias in the last parsed thrift file. False otherwise.
        :rtype: bool

        """
        return alias in self._result.typedefs

    def get_typedef(self, alias):
        """ Returns the thrift type for the given alias according to the typedefs found in the last parse.

        :param alias: The alias of the typedef to check for.
        :type alias: str
        :returns: The thrift type for the given alias according to the typedefs in the last parsed thrift file.
        :raises: KeyError

        """
        return self._result.typedefs[alias]

    def unalias_type(self, field_type):
        """ Returns the unaliased thrift type according to the typedefs found in the last parse.

        :param field_type: The potentially aliased thrift type.
        :type field_type: str
        :returns: The unaliased thrift type according to the typedefs in the last parsed thrift file.
        :raises: ThriftCLIException

        """
        type_set = set([field_type])
        while self.has_typedef(field_type):
            field_type = self.get_typedef(field_type)
            if field_type in type_set:
                raise thrift_cli.ThriftCLIException('Circular typedef dependency involving \'%s\'' % field_type)
            type_set.add(field_type)
        return field_type
