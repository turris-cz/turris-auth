#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
import argparse
import cgi
import cgitb
import contextlib
import datetime
import fcntl
import http
import http.cookies
import os
import random
import string
import sys
import time
import typing
from pathlib import Path

import euci
import pbkdf2
from jinja2 import Template

cgitb.enable()

COOKIELEN = 64
TIMEOUT = 36000
TRUSTFILE = Path("/var/run/lighttpd-turris-auth.trust")
LOGIN_PAGE = Path(__file__).parent / "login.html.j2"


@contextlib.contextmanager
def trustlist():
    """Provides access to all trusted clients.
    The trust file contains lines of TIME:COOKIE. The TIME is number of seconds since epoch when the cookie was used the
    last time and the COOKIE is a string of 64 characters we use to trust user.
    This function has to be used in "with" statement and it holds key to trust file for whole context duration. This is
    because any modifications to dictionary provided by this function are written back to file after context exit.
    Returns dictionary where keys are COOKIE strings and values are integers TIME.
    """
    now = time.time()
    with TRUSTFILE.open("r+" if TRUSTFILE.exists() else "w+") as file:
        fcntl.flock(file.fileno(), fcntl.LOCK_EX)
        trust = {}
        file.seek(0, os.SEEK_SET)
        for line in file:
            used, cookie = line.strip().split(":", maxsplit=1)
            used = int(used)
            if now <= used + TIMEOUT:
                trust[cookie] = used
        yield trust
        file.seek(0, os.SEEK_SET)
        file.truncate()
        for cookie, used in trust.items():
            file.write(f"{used}:{cookie}\n")
        file.flush()
        fcntl.flock(file.fileno(), fcntl.LOCK_UN)


def verify_cookie(cookie):
    """Verify the cookie against list of trusted ones."""
    with trustlist() as trust:
        if cookie in trust:
            trust[cookie] = int(time.time())
            return True
    return False


def verify_password(password):
    """Verify password."""
    uci = euci.EUci()
    # Note: no password means no login is required.
    password_hash = uci.get("turris-auth", "admin", "password", default="")
    if not password_hash:
        password_hash = uci.get("foris", "auth", "password", default="")
    return not password_hash or password_hash == pbkdf2.crypt(password, salt=password_hash)


########################################################################################################################
def http_header(
    httpstatus: http.HTTPStatus,
    values: typing.Dict[str, str],
    cookies: typing.Optional[http.cookies.SimpleCookie] = None,
):
    """Prints HTTP header including the terminating new line."""
    response = [f"Status: {httpstatus.value} {httpstatus.phrase}"]
    for key, value in values.items():
        response.append(f"{key}: {value}")
    if cookies is not None:
        response.append(str(cookies))
    print("\n".join(response))
    print("")


def login_page(wrongpass=False):
    http_header(
        http.HTTPStatus.OK,
        {
            "Content-type": "text/html",
        },
    )
    with LOGIN_PAGE.open("r") as file:
        print(Template(file.read()).render(wrongpass=wrongpass))


def login_get():
    query = cgi.parse()
    curcookie = http.cookies.SimpleCookie(os.getenv("HTTP_COOKIE"))
    if curcookie.get("turrisauth") and verify_cookie(curcookie["turrisauth"].value):
        http_header(http.HTTPStatus.FOUND, {"Location": query.get("orig", ["/"])[0]})
    else:
        login_page()


def login_post():
    query = cgi.parse()
    form = cgi.FieldStorage()
    if not verify_password(form["password"].value.encode()):
        return login_page(wrongpass=True)

    cookie = "".join(random.choice(string.ascii_lowercase) for i in range(COOKIELEN))
    with trustlist() as trust:
        trust[cookie] = int(time.time())
    c = http.cookies.SimpleCookie()
    c["turrisauth"] = cookie
    c["turrisauth"]["expires"] = "true"
    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    c["turrisauth"]["expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
    if os.getenv("REQUEST_SCHEME") == "http":
        c["turrisauth"]["httponly"] = "true"
    else:
        c["turrisauth"]["secure"] = "true"
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 8:
        c["turrisauth"]["samesite"] = "Strict"
    http_header(http.HTTPStatus.SEE_OTHER, {"Location": query.get("orig", ["/"])[0]}, c)


def login():
    {"GET": login_get, "POST": login_post}[os.getenv("REQUEST_METHOD", default="GET")]()


def logout():
    curcookie = http.cookies.SimpleCookie(os.getenv("HTTP_COOKIE"))
    if curcookie.get("turrisauth"):
        with trustlist() as trust:
            if curcookie["turrisauth"].value in trust:
                del trust[curcookie["turrisauth"].value]
    c = http.cookies.SimpleCookie()
    c["turrisauth"] = ""
    c["turrisauth"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"
    http_header(http.HTTPStatus.SEE_OTHER, {"Location": "/"}, c)


########################################################################################################################
def main():
    parser = argparse.ArgumentParser(description="Lighttpd authentication for Turris")
    parser.add_argument("--verify", help="Verify given cookie.")
    args = parser.parse_args()

    if args.verify:
        sys.exit(0 if verify_cookie(args.verify) else 1)
    {"/login": login, "/logout": logout}[os.getenv("SCRIPT_NAME", default="/login")]()


if __name__ == "__main__":
    main()
