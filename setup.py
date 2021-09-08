#!/usr/bin/env python3
from setuptools import setup

setup(
    name='lighttpd-turris-auth',
    version='0.2.0',
    description="Lighttpd Turris Authenticator",
    url="https://gitlab.nic.cz/turris/lighttpd-turris-auth",
    author="CZ.NIC, z. s. p. o.",
    author_email="packaging@turris.cz",
    license="GPL-3.0-or-later",

    packages=['lighttpd_turris_auth', 'lighttpd_turris_auth.server'],
    package_data={
        'lighttpd_turris_auth.server': ['templates/*.j2', 'resources/**']
    },
    entry_points={
        'console_scripts': [
            'set-turris-auth = lighttpd_turris_auth.__main__:main',
            'lighttpd-turris-auth-server = lighttpd_turris_auth.server.__main__:main'
        ]
    },
    install_requires=[
        "pbkdf2",
        "jinja2",
        "pyuci @ git+https://gitlab.nic.cz/turris/pyuci.git",
    ],
)
