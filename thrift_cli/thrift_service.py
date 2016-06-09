class ThriftService(object):
    class Endpoint(object):

        def __init__(self, return_type, name, fields=[], oneway=False):
            self.return_type = return_type
            self.name = name
            self.fields = fields
            self.oneway = True if oneway else False

        def __eq__(self, other):
            if not type(other) is type(self):
                return False
            if self.return_type != other.return_type:
                return False
            if self.name != other.name:
                return False
            if self.oneway != other.oneway:
                return False
            for self_field, other_field in zip(self.fields, other.fields):
                if self_field != other_field:
                    return False
            return True

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            fields_list = ', '.join([str(field) for field in self.fields.values()])
            str_params = ('oneway ' if self.oneway else '', self.return_type, self.name, fields_list)
            return '%s%s %s(%s)' % str_params

    def __init__(self, name, endpoints):
        self.name = name
        self.endpoints = endpoints

    def __eq__(self, other):
        return type(other) is type(self) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '%s ' % self.name + ''.join(['\n\t%s' % str(endpoint) for endpoint in self.endpoints.values()])
