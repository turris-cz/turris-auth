# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""This simplifies and caches access to pages generated from templates.
"""
import functools
import pathlib

import jinja2

TEMPLATES = pathlib.Path(__file__).parent / "templates"


class Pages:
    """Generated pages with caching for those being constant."""

    LOGIN = "login.html.j2"

    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.PackageLoader(__package__, "templates"), autoescape=jinja2.select_autoescape(["html"])
        )
        self._login = self.env.get_template(self.LOGIN)

    @functools.lru_cache()
    def login(self, wrongpass: bool = False, insecure: bool = True) -> str:
        """Login page for entering password and other login information for authentication."""
        return self._login.render(wrongpass=wrongpass, insecure=insecure)
