class ThriftService(object):
    """ Provides a representation of a service declared in thrift. """

    class Endpoint(object):
        def __init__(self, return_type, name, fields={}, oneway=False):
            self.return_type = return_type
            self.name = name
            self.fields = fields
            self.oneway = True if oneway else False

        def __eq__(self, other):
            return type(other) is type(self) and self.__dict__ == other.__dict__

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            fields_list = ', '.join([str(field) for field in self.fields.values()])
            str_params = ('oneway ' if self.oneway else '', self.return_type, self.name, fields_list)
            return '%s%s %s(%s)' % str_params

    def __init__(self, reference, endpoints):
        """
        :param reference: A unique reference to the struct, defined as 'Namespace.name'.
        :param endpoints: A dictionary from endpoint names to endpoint objects that compromise the service.
        """
        self.reference = reference
        self.endpoints = endpoints

    def __eq__(self, other):
        return type(other) is type(self) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '%s ' % self.reference + ''.join(['\n\t%s' % str(endpoint) for endpoint in self.endpoints.values()])
