# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2022, CZ.NIC z.s.p.o. (http://www.nic.cz/)

import pathlib

from turris_auth.luci import prepare_acls

ACL_DIR = pathlib.Path(__file__).parent / "acl.d"


def test_prepare_acls():
    assert prepare_acls(ACL_DIR) == {
        "access-group": {
            "luci-access": ["read", "write"],
            "uci-access": ["read", "write"],
            "unauthenticated": ["read"],
        },
        "file": {
            "/": ["list"],
            "/bin/kill": ["exec"],
            "/etc/crontabs/root": ["read", "write"],
        },
        "ubus": {
            "file": ["list", "read", "stat", "write", "remove", "exec"],
            "session": ["access", "login"],
            "uci": [
                "changes",
                "get",
                "add",
                "apply",
                "confirm",
                "delete",
                "order",
                "set",
                "rename",
            ],
        },
        "uci": {
            "*": ["read", "write"],
        },
    }
