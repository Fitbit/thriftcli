from .thrift_cli_error import ThriftCLIError


class ThriftParseResult(object):
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
        """ Add the definitions from another ThriftParseResult into this one. """
        self.merge_structs(other.structs)
        self.merge_services(other.services)
        self.merge_enums(other.enums)
        self.merge_typedefs(other.typedefs)

    def merge_structs(self, structs):
        """ Add the structs from another ThriftParseResult into this one. """
        self.structs.update(structs)

    def merge_services(self, services):
        """ Add the services from another ThriftParseResult into this one. """
        self.services.update(services)

    def merge_enums(self, enums):
        """ Add the enums from another ThriftParseResult into this one. """
        self.enums.update(enums)

    def merge_typedefs(self, typedefs):
        """ Add the typedefs from another ThriftParseResult into this one. """
        self.typedefs.update(typedefs)

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
        return self.services[service_reference].endpoints[method_name].fields

    def get_fields_for_struct_name(self, struct_name):
        """ Returns all fields that compromise the given struct.
    
        :param struct_name: The name of the struct.
        :type struct_name: str
        :returns: Fields that are declared as components for the provided struct.
        :rtype: list of ThriftStruct.Field
        :raises: KeyError, AttributeError
    
        """
        return self.structs[struct_name].fields

    def has_enum(self, enum_name):
        """ Checks if the given enum was found in the last parse.
    
        :param enum_name: The name of the enum to check for.
        :type enum_name: str
        :returns: True if the enum was declared in the last parsed thrift file. False otherwise.
        :rtype: bool
    
        """
        if not self:
            return False
        return enum_name in self.enums

    def get_struct(self, struct_name):
        """ Returns the struct for the given struct name.
    
        :param struct_name: The name of the struct to look up.
        :type struct_name: str
        :returns: The associated ThriftStruct or None.
        :rtype: ThriftStruct or None
    
        """
        if not self or struct_name not in self.structs:
            return None
        return self.structs[struct_name]

    def get_typedef(self, alias):
        """ Returns the thrift type for the given alias according to the typedefs found in the last parse.
    
        :param alias: The alias of the typedef to check for.
        :type alias: str
        :returns: The thrift type for the given alias according to the typedefs in the last parsed thrift file.
        :rtype: str or None
    
        """
        if not self or alias not in self.typedefs:
            return None
        return self.typedefs[alias]

    def unalias_type(self, field_type):
        """ Returns the unaliased thrift type according to the typedefs found in the last parse.
    
        :param field_type: The potentially aliased thrift type.
        :type field_type: str
        :returns: The unaliased thrift type according to the typedefs in the last parsed thrift file.
        :raises: ThriftCLIError
    
        """
        type_set = {field_type}
        while self.get_typedef(field_type) is not None:
            field_type = self.get_typedef(field_type)
            if field_type in type_set:
                raise ThriftCLIError('Circular typedef dependency involving \'%s\'' % field_type)
            type_set.add(field_type)
        return field_type
