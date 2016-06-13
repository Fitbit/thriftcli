try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Thrift CLI',
    'author': 'Neel Virdy',
    'version': '0.1',
    'packages': ['thriftcli'],
    'scripts': [],
    'name': 'thriftcli'
}

setup(**config)
