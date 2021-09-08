# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
import euci
import pbkdf2

PASSWORD_ITERATIONS = 1000


def assign(password: str) -> None:
    """Sets given password as the password for turris-auth."""
    new_password_hash = pbkdf2.crypt(password, iterations=PASSWORD_ITERATIONS)
    with euci.EUci() as uci:
        uci.set("turris-auth", "admin", "auth")
        uci.set("turris-auth", "admin", "password", new_password_hash)


def verify(password: str) -> bool:
    """Verify password."""
    uci = euci.EUci()
    password_hash = uci.get("turris-auth", "admin", "password", default="")
    if not password_hash:
        # We check previous Foris password as well for backward compatibility
        password_hash = uci.get("foris", "auth", "password", default="")
    # Note: no password means no login is required.
    return not password_hash or password_hash == pbkdf2.crypt(password.encode(), salt=password_hash)
