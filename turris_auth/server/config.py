# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021-2024, CZ.NIC z.s.p.o. (https://www.nic.cz/)
"""Lighttpd's dynamic configuration.
We need dynamic configuration to be independent on resources installation location (as that is given by setuptools).
"""

import shutil


def _server(authorizer: bool, luci_login: bool) -> str:
    return f"""(
    "socket" => "/tmp/fastcgi.turris_auth.socket",
    "bin-path" => "{shutil.which('turris-auth-server')}",
    "bin-environment" => ( "TURRIS_AUTH_LUCI" => "{luci_login}" ),
    "check-local" => "disable",
    "min-procs" => 0,
    "max-procs" => 1,
    "idle-timeout" => 180,
    "mode" => "{'authorizer' if authorizer else 'responder'}",
)"""


def config(luci_login: bool) -> str:
    """Returns string with desired Lighttpd configuration."""
    return f"""# Automatically generated configuration for turris-auth.
var.turris_auth_scriptname = "turris-auth"
var.turris_auth = {_server(True, luci_login)}
var.turris_auth_responder = ( turris_auth_scriptname => {_server(False, luci_login)})

fastcgi.server += (
    "/login" => turris_auth_responder,
    "/logout" => turris_auth_responder,
    "/login.json" => turris_auth_responder,
    "/extend-session" => turris_auth_responder,
)"""
