import re

from setuptools import setup


def make_version_unique(version):
    if version.exact:
        return version.format_with('{tag}+{time:%s}')
    else:
        return version.format_with('{tag}.post{distance}+{time:%s}')

config = {
    'name': 'thriftcli',
    'description': 'Thrift CLI',
    'author': 'Neel Virdy',
    'packages': ['thriftcli'],
    'entry_points': {
        'console_scripts': ['thriftcli = thriftcli.thrift_cli:main']
    },
    'install_requires': ['thrift', 'kazoo', 'mock'],
    'requires': ['thrift', 'kazoo', 'mock'],
    'use_scm_version': {'version_scheme': make_version_unique},
    'setup_requires': ['setuptools_scm']
}

setup(**config)
