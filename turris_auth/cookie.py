# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""The cookies management functions.
"""
import contextlib
import datetime
import fcntl
import http.cookies
import os
import pathlib
import random
import string
import time
import typing

from . import luci

KEY = "turrisauth"
LUCI_KEY = "sysauth_http"
LUCI_SECURE_KEY = "sysauth_https"
TRUSTFILE = pathlib.Path("/var/run/turris-auth.trust")
TIMEOUT = 600
LENGTH = 64


@contextlib.contextmanager
def trustlist(readonly: bool = False) -> dict[str, int]:
    """Provides access to all trusted clients.
    The trust file contains lines of TIME:COOKIE. The TIME is number of seconds since epoch when the cookie was used the
    last time and the COOKIE is a string of 64 characters we use to trust user.
    This function has to be used in "with" statement and it holds key to trust file for whole context duration. This is
    because any modifications to dictionary provided by this function are written back to file after context exit
    (unless ro argument is True).
    Returns dictionary where keys are COOKIE strings and values are integers TIME.
    """
    now = time.time()
    try:
        with TRUSTFILE.open("r" if readonly else "a+") as file:
            fcntl.flock(file.fileno(), fcntl.LOCK_SH if readonly else fcntl.LOCK_EX)
            trust = {}

            file.seek(0, os.SEEK_SET)
            for line in file:
                used, cookie = line.strip().split(":", maxsplit=1)
                used = int(used)
                if now <= used + TIMEOUT:  # This automatically drops obsolete cookies
                    trust[cookie] = used

            yield trust

            if not readonly:
                file.seek(0, os.SEEK_SET)
                file.truncate()
                for cookie, used in trust.items():
                    file.write(f"{used}:{cookie}\n")
    except FileNotFoundError:
        yield {}


def generate(secure: bool, luci_login: bool) -> http.cookies.SimpleCookie:
    """Generates a new cookie.
    To correctly configure cookie the information if secure connection is used or not is required to be provided.
    Returns instance of http.cookies.SimpleCookie.
    """
    cookie = "".join(random.choice(string.ascii_lowercase) for i in range(LENGTH))
    with trustlist() as trust:
        trust[cookie] = int(time.time())

    httpcookie = http.cookies.SimpleCookie()
    httpcookie[KEY] = cookie
    if secure:
        httpcookie[KEY]["secure"] = "true"
    else:
        httpcookie[KEY]["httponly"] = "true"

    httpcookie[KEY]["samesite"] = "Strict"

    # set luci key
    if luci_login:
        if secure:
            httpcookie[LUCI_SECURE_KEY] = luci.create_session(60 * 15)
        else:
            httpcookie[LUCI_KEY] = luci.create_session(60 * 15)

    return httpcookie


def remove(cookies: str, luci_login: bool) -> http.cookies.SimpleCookie:
    """Removes cookie (not fails if cookie is invalid).
    Removes instance of http.cookie.SimpleCookie that can be send to client to remove existing cookie from storage.
    """
    cookie = http.cookies.SimpleCookie(cookies).get(KEY)
    luci_cookie = http.cookies.SimpleCookie(cookies).get(LUCI_KEY)
    luci_secure_cookie = http.cookies.SimpleCookie(cookies).get(LUCI_SECURE_KEY)
    if cookie is not None:
        with trustlist() as trust:
            if cookie.value in trust:
                del trust[cookie.value]

    httpcookie = http.cookies.SimpleCookie()
    httpcookie[KEY] = ""
    httpcookie[KEY]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"

    with open("/tmp/remove", 'w') as f:
        f.write(f"{luci_login} {httpcookie}")

    if luci_login:
        if luci_cookie is not None:
            luci.destroy_session(luci_cookie.value)
            httpcookie[LUCI_KEY] = ""
            httpcookie[LUCI_KEY]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
        if luci_secure_cookie is not None:
            luci.destroy_session(luci_secure_cookie.value)
            httpcookie[LUCI_SECURE_KEY] = ""
            httpcookie[LUCI_SECURE_KEY]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"

    return httpcookie


def verify(cookies: str, luci_login: bool) -> bool:
    """Verify the cookie against list of trusted ones."""
    cookie = http.cookies.SimpleCookie(cookies).get(KEY)
    if cookie is not None:
        with trustlist() as trust:
            if cookie.value in trust:
                trust[cookie.value] = int(time.time())

                if luci_login:
                    luci_cookie = http.cookies.SimpleCookie(cookies).get(LUCI_KEY)
                    if luci_cookie:
                        luci.touch_session(luci_cookie)
                    luci_cookie = http.cookies.SimpleCookie(cookies).get(LUCI_SECURE_KEY)
                    if luci_cookie:
                        luci.touch_session(luci_cookie)

                return True

    return False


def last_use(cookies: str) -> typing.Optional[datetime.datetime]:
    """Get time of last use of cookies (or None if cookies are invalid)."""
    cookie = http.cookies.SimpleCookie(cookies).get(KEY)
    if cookie is not None:
        with trustlist(readonly=True) as trust:
            if cookie.value in trust:
                return datetime.datetime.fromtimestamp(int(trust[cookie.value]))
    return None
