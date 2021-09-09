# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""Fast CGI implementation for login gateway.
"""
import cgi
import cgitb
import http
import json
import logging
import sys

import flup.server.fcgi
import flup.server.fcgi_base

from .. import cookie, password
from . import pages

logger = logging.getLogger(__package__)

STATUS_OK = f"{http.HTTPStatus.OK.value} {http.HTTPStatus.OK.phrase}"
STATUS_FOUND = f"{http.HTTPStatus.FOUND.value} {http.HTTPStatus.FOUND.phrase}"
STATUS_SEE_OTHER = f"{http.HTTPStatus.SEE_OTHER.value} {http.HTTPStatus.SEE_OTHER.phrase}"
STATUS_UNAUTHORIZED = f"{http.HTTPStatus.UNAUTHORIZED.value} {http.HTTPStatus.UNAUTHORIZED.phrase}"
STATUS_NOT_FOUND = f"{http.HTTPStatus.NOT_FOUND.value} {http.HTTPStatus.NOT_FOUND.phrase}"
STATUS_SERVER_ERROR = f"{http.HTTPStatus.INTERNAL_SERVER_ERROR.value} {http.HTTPStatus.INTERNAL_SERVER_ERROR.phrase}"


class Server:
    """The turris-auth fast CGI server implementation."""

    def __init__(self, report_invalid_password: bool = False):
        self.report_invalid_password = report_invalid_password
        self.wsgi = flup.server.fcgi.WSGIServer(
            self._main, roles=(flup.server.fcgi_base.FCGI_RESPONDER, flup.server.fcgi_base.FCGI_AUTHORIZER)
        )
        self.pages = pages.Pages()

    def run(self):
        """Run the WSGI server"""
        return self.wsgi.run()

    def _main(self, environ, start_response):
        # The CONTENT_LENGTH is not available for FCGI_AUTHORIZER
        if "CONTENT_LENGTH" in environ:
            # Responder
            try:
                return {
                    "GET/login": self._login,
                    "POST/login": self._login_post,
                    "GET/logout": self._logout,
                    "GET/login.json": self._status,
                }[f"{environ['REQUEST_METHOD']}{environ['SCRIPT_NAME']}"](environ, start_response)
            except KeyError:
                # The access to anything that is not implemented here is an error in configuration
                logger.error("(%s) Accessing unimplemented URL: %s", environ["REMOTE_ADDR"], environ["SCRIPT_NAME"])
                start_response(STATUS_NOT_FOUND, [("Content-type", "text/plain")])
                return ["404 Not found"]
            except Exception:
                start_response(STATUS_SERVER_ERROR, [("Content-type", "text/html")])
                # TODO append info where to submit the issue
                return [cgitb.html(sys.exc_info())]

        # Authorizer
        if cookie.verify(environ.get("HTTP_COOKIE")):
            start_response(STATUS_OK, [])
        else:
            if (environ.get("HTTP_X_REQUESTED_WITH") or "") == "":
                start_response(STATUS_SEE_OTHER, [("Location", f"/login?{environ['REQUEST_URI']}")])
            else:  # X-Requested-With header is not used by browser but should be specified by AJAX requests
                start_response(STATUS_UNAUTHORIZED, [])
        return []

    def _login(self, environ, start_response):
        if cookie.verify(environ.get("HTTP_COOKIE")):
            start_response(STATUS_FOUND, [("Location", environ.get("QUERY_STRING") or "/")])
            return []
        # We allow here any origin as we are attempting redirect to https which is cross-site
        start_response(STATUS_OK, [("Content-type", "text/html"), ("Access-Control-Allow-Origin", "*")])
        return [self.pages.login(insecure=environ["REQUEST_SCHEME"] == "http")]

    def _login_post(self, environ, start_response):
        form = cgi.FieldStorage(fp=environ["wsgi.input"], environ=environ)
        password2check = form["password"].value
        if not password.verify(password2check):
            logger.info(
                "(%s) Attempt to login with invalid password%s",
                environ["REMOTE_ADDR"],
                f": {password2check}" if self.report_invalid_password else "",
            )
            start_response(STATUS_UNAUTHORIZED, [("Content-type", "text/html")])
            return self.pages.login(wrongpass=True, insecure=environ["REQUEST_SCHEME"] == "http")

        httpcookie = cookie.generate(secure=environ["REQUEST_SCHEME"] == "https")
        start_response(
            STATUS_FOUND,
            [
                ("Location", environ.get("QUERY_STRING") or "/"),
                ("Set-Cookie", httpcookie.output(header="")),
            ],
        )
        return []

    @staticmethod
    def _logout(environ, start_response):
        httpcookie = cookie.remove(environ.get("HTTP_COOKIE"))
        start_response(STATUS_FOUND, [("Location", "/"), ("Set-Cookie:", httpcookie.output(header=""))])
        return []

    @staticmethod
    def _status(environ, start_response):
        last_cookie_use = cookie.last_use(environ.get("HTTP_COOKIE"))
        res = json.dumps({"accesstime": int(last_cookie_use.timestamp()) if last_cookie_use else None})
        start_response(STATUS_OK, [("Content-type", "test/json"), ("Access-Control-Allow-Origin", "*")])
        return [res]
