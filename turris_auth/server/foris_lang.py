"""The language configured in Foris.
"""
import time

import euci


def foris_language():
    """Function to fetch foris language."""
    now = time.monotonic()
    if foris_language.last_fetch is None or foris_language.last_fetch + 120 < now:
        uci = euci.EUci()
        foris_language.lang = uci.get("foris", "settings", "lang", default=None)
        foris_language.last_fetch = now
    return foris_language.lang


foris_language.lang = None
foris_language.last_fetch = None
