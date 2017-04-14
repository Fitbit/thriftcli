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

class ThriftService(object):
    """ Provides a representation of a service declared in thrift. """

    class Endpoint(object):
        def __init__(self, return_type, name, fields=None, oneway=False):
            self.return_type = return_type
            self.name = name
            self.fields = fields if fields is not None else {}
            self.oneway = True if oneway else False

        def __eq__(self, other):
            return type(other) is type(self) and self.__dict__ == other.__dict__

        def __ne__(self, other):
            return not self.__eq__(other)

        def __str__(self):
            fields_list = ', '.join([str(field) for field in self.fields.values()])
            str_params = ('oneway ' if self.oneway else '', self.return_type, self.name, fields_list)
            return '%s%s %s(%s)' % str_params

    def __init__(self, reference, endpoints, extends=None):
        """
        :param reference: a unique reference to the service, defined as 'Namespace.name'.
        :param endpoints: a dictionary from endpoint names to endpoint objects that compromise the service.
        :param extends: a unique reference to the service that this service extends, or None.
        """
        self.reference = reference
        self.endpoints = endpoints
        self.extends = extends

    def __eq__(self, other):
        return type(other) is type(self) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.reference + (' extends %s' % self.extends if self.extends is not None else '') + \
               ''.join(['\n\t%s' % str(endpoint) for endpoint in self.endpoints.values()])
