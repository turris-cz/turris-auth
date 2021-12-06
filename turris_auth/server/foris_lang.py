# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""The language configured in Foris.
"""
import time
import typing

import euci


def foris_language() -> typing.Optional[str]:
    """Function to fetch foris language."""
    now = time.monotonic()
    if foris_language.last_fetch is None or foris_language.last_fetch + 120 < now:
        uci = euci.EUci()
        foris_language.lang = uci.get("foris", "settings", "lang", default="") or None
        foris_language.last_fetch = now
    return foris_language.lang


foris_language.lang = None
foris_language.last_fetch = None
