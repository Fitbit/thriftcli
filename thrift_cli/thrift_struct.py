import thrift_cli

class ThriftStruct(object):

	class Field(object):

		def __init__(self, index, field_type, name, **kwargs):
			self.index = int(index)
			self.field_type = field_type
			self.name = name
			self.default = kwargs.get('default', None)
			if 'required' in kwargs and 'optional' in kwargs and kwargs['optional'] == kwargs['required']:
				raise thrift_cli.ThriftCLIException('Contradicting modifiers on required and optional for field - %s:%s %s' % (index, field_type, name))
			self.optional = kwargs.get('optional', True) and not ('required' in kwargs and kwargs['required'])
			self.required = not self.optional and kwargs.get('required', True)
			self.modifier = 'required' if self.required else 'optional' if kwargs.get('optional', False) else ''

		def __eq__(self, other):
			return type(other) is type(self) and self.__dict__ == other.__dict__

		def __ne__(self, other):
			return not self.__eq__(other)

		def __str__(self):
			modifier_str = ('%s ' % self.modifier) if self.modifier else ''
			default_str = (' = %s' % str(self.default)) if self.default != None else ''
			str_params = (self.index, modifier_str, self.field_type, self.name, default_str)
			return '%s:%s%s %s%s' % str_params

	def __init__(self, name, fields):
		self.name = name
		self.fields = fields

	def __eq__(self, other):
		if not type(other) is type(self):
			return False
		if self.name != other.name:
			return False
		for self_field, other_field in zip(self.fields, other.fields):
			if self_field != other_field:
				return False
		return True

	def __ne__(self, other):
		return not self.__eq__(other)

	def __str__(self):
		return '%s ' % self.name + ''.join(['\n\t%s' % str(field) for field in self.fields.values()])