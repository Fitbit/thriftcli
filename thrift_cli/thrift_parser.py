import re

from .thrift_service import ThriftService
from .thrift_struct import ThriftStruct


class ThriftParser(object):
    class Result(object):
        def __init__(self, structs, services):
            self.structs = structs
            self.services = services

        def __eq__(self, other):
            return type(other) is type(self) and self.__dict__ == other.__dict__

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            return str({
                'structs': {name: str(struct) for name, struct in self.structs.items()},
                'services': {name: str(service) for name, service in self.services.items()}
            })

    def __init__(self):
        self._thrift_path = None
        self._thrift_content = None
        self.structs_regex = re.compile(r'^([\r\t ]*?struct (\w+)[^}]+})', flags=re.MULTILINE)
        self.services_regex = re.compile(r'^([\r\t ]*?service (\w+)[^}]+})', flags=re.MULTILINE)
        self.endpoints_regex = re.compile(r'^[\r\t ]*(oneway)?\s*(\w+)\s*(\w+)\(([a-zA-Z0-9: ,]*)\)',
                                          flags=re.MULTILINE)
        self.fields_regex = re.compile(
            r'^[\r\t ]*([\d+]):\s*(optional|required)?\s*(\w+)?\s*(\w+)(?:\s*=\s*([^,\s]+))?', flags=re.MULTILINE)

    def parse(self, thrift_path):
        self._thrift_path = thrift_path
        self._thrift_content = self._load_file(thrift_path)
        return ThriftParser.Result(self._parse_structs(), self._parse_services())

    def _load_file(self, path):
        with open(path, 'r') as file:
            return file.read()

    def _parse_structs(self):
        definitions_by_name = self._parse_struct_definitions()
        fields_by_name = {name: self._parse_fields_from_struct_definition(definition) for name, definition in
                          definitions_by_name.items()}
        structs = {name: ThriftStruct(name, fields) for name, fields in fields_by_name.items()}
        return structs

    def _parse_struct_definitions(self):
        structs_list = self.structs_regex.findall(self._thrift_content)
        structs = {name: definition for (definition, name) in structs_list}
        return structs

    def _parse_fields_from_struct_definition(self, definition):
        field_matches = self.fields_regex.findall(definition)
        fields = [self._construct_field_from_field_match(field_match) for field_match in field_matches]
        fields = {field.name: field for field in fields}
        return fields

    def _parse_services(self):
        definitions_by_name = self._parse_service_definitions()
        endpoints_by_name = {name: self._parse_endpoints_from_service_definition(definition) for name, definition in
                             definitions_by_name.items()}
        services = {name: ThriftService(name, endpoints) for name, endpoints in endpoints_by_name.items()}
        return services

    def _parse_service_definitions(self):
        services_list = self.services_regex.findall(self._thrift_content)
        services = {name: definition for (definition, name) in services_list}
        return services

    def _parse_endpoints_from_service_definition(self, definition):
        endpoint_matches = self.endpoints_regex.findall(definition)
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
        field_strings = [field_string.strip() for field_string in fields_string.split(',')]
        field_matches = [self.fields_regex.findall(field_string) for field_string in field_strings]
        field_matches = [field_match[0] for field_match in field_matches if len(field_match)]
        fields = [self._construct_field_from_field_match(field_match) for field_match in field_matches]
        return fields

    @staticmethod
    def _construct_field_from_field_match(field_match):
        (index, oneway, return_type, name, default) = field_match
        oneway = oneway == 'oneway'
        default = default if len(default) else None
        return ThriftStruct.Field(index, return_type, name, oneway=oneway, default=default)
