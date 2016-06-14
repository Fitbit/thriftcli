import thrift_cli


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
                raise thrift_cli.ThriftCLIException(
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

    def __init__(self, name, fields={}):
        self.name = name
        self.fields = fields

    def __eq__(self, other):
        return type(other) is type(self) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        sorted_fields = sorted(self.fields.values(), key=lambda field: field.index)
        return '%s ' % self.name + ''.join(['\n\t%s' % str(field) for field in sorted_fields])
