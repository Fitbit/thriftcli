import re

from setuptools import setup

version = re.search(
    '^__version__\s*=\s*\'(.*)\'',
    open('thriftcli/thrift_cli.py').read(),
    flags=re.MULTILINE
).group(1)

config = {
    'name': 'thriftcli',
    'description': 'Thrift CLI',
    'author': 'Neel Virdy',
    'version': version,
    'packages': ['thriftcli'],
    'entry_points': {
        'console_scripts': ['thriftcli = thriftcli.thrift_cli:main']
    },
    'install_requires': ['thrift', 'mock'],
    'requires': ['thrift', 'mock']
}

setup(**config)
