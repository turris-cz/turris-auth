# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""Lighttpd's dynamic configuration.
We need dynamic configuration to be independent on resources installation location (as that is given by setuptools).
"""
import pathlib
import shutil

RESOURCES = pathlib.Path(__file__).parent / "resources"


def _server(authorizer: bool) -> str:
    return f"""(
    "socket" => "/tmp/fastcgi.turris_auth.socket",
    "bin-path" => "{shutil.which('turris-auth-server')}",
    "check-local" => "disable",
    "min-procs" => 0,
    "max-procs" => 1,
    "idle-timeout" => 180,
    "mode" => "{'authorizer' if authorizer else 'responder'}",
)"""


def config() -> str:
    """Returns string with desired Lighttpd configuration."""
    return f"""# Automatically generated configuration for turris-auth.
var.turris_auth_scriptname = "turris-auth"
var.turris_auth = {_server(True)}
var.turris_auth_responder = ( turris_auth_scriptname => {_server(False)})

alias.url += (
    "/turris-auth" => "{RESOURCES}"
)
fastcgi.server += (
    "/login" => turris_auth_responder,
    "/logout" => turris_auth_responder,
    "/login.json" => turris_auth_responder,
)"""
