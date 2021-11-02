#!/usr/bin/env python3
from setuptools import setup

setup(
    name='turris-auth',
    version='0.2.0',
    description="Turris Authenticator for web applications",
    url="https://gitlab.nic.cz/turris/turris-auth",
    author="CZ.NIC, z. s. p. o.",
    author_email="packaging@turris.cz",
    license="GPL-3.0-or-later",

    packages=['turris_auth', 'turris_auth.server'],
    package_data={
        'turris_auth.server': ['templates/*.j2', 'resources/**']
    },
    entry_points={
        'console_scripts': [
            'set-turris-auth = turris_auth.__main__:main',
            'turris-auth-server = turris_auth.server.__main__:main'
        ]
    },
    install_requires=[
        "pbkdf2",
        "jinja2",
        "flup",
        "pyuci @ git+https://gitlab.nic.cz/turris/pyuci.git",
    ],
)
