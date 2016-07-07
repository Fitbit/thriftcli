import re

from setuptools import setup

module_version = re.search(
    '^__version__\s*=\s*\'(.*)\'',
    open('thriftcli/thrift_cli.py').read(),
    flags=re.MULTILINE
).group(1)


def make_version_unique(version):
    if version.exact:
        return version.format_with('{tag}+{time:%s}')
    else:
        return version.format_with('{tag}.post{distance}+{time:%s}')

config = {
    'name': 'thriftcli',
    'description': 'Thrift CLI',
    'author': 'Neel Virdy',
    'version': module_version,
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
