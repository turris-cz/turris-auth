# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""This simplifies and caches access to pages generated from templates.
"""
import functools
import gettext
import pathlib
import typing

import jinja2

TEMPLATES = pathlib.Path(__file__).parent / "templates"
LOCALE = pathlib.Path(__file__).parent / "locale"


class Pages:
    """Generated pages with caching for those being constant."""

    LOGIN = "login.html.j2"

    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.PackageLoader(__package__, "templates"),
            autoescape=jinja2.select_autoescape(["html"]),
            extensions=["jinja2.ext.i18n"],
        )
        self.translations = {}
        self._lang(None)

        self._login = self.env.get_template(self.LOGIN)

    @functools.lru_cache()
    def login(self, lang: typing.Optional[str], wrongpass: bool = False, insecure: bool = True) -> bytes:
        """Login page for entering password and other login information for authentication."""
        self._lang(lang)
        return self._login.render(lang=lang, wrongpass=wrongpass, insecure=insecure).encode()

    def _lang(self, lang):
        if lang not in self.translations:
            self.translations[lang] = gettext.translation(
                "turris_auth.server", LOCALE, languages=[lang] if lang is not None else None, fallback=True
            )
        self.env.install_gettext_translations(self.translations[lang])
