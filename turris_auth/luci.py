# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2022, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""Luci session management helpers
"""
import functools
import json
import pathlib
import secrets
import typing

DEFAULT_ACL_DIR = pathlib.Path("/usr/share/rpcd/acl.d/")


def ubus_connected(func: typing.Callable) -> typing.Callable:
    """Makes sure that this wrapped function is call when ubus is connected"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import ubus

        if not ubus.get_connected():
            ubus.connect()
        return func(*args, **kwargs)

    return wrapper


def prepare_acls(dir: pathlib.Path = DEFAULT_ACL_DIR) -> typing.Dict:
    """Parses ACL which would be granted to Luci session via rpcd

    It should reimplement the code from rpcd in python

    see https://git.openwrt.org/?p=project/rpcd.git;a=blob;f=session.c;h=c7d9f3202e6beba81e43ccaff2a7f8e3ba18c3bb;hb=HEAD#l1080
    """
    res: typing.Dict = {"access-group": {}}
    for path in dir.glob("*.json"):
        with path.open() as f:
            parsed = json.load(f)

        for group, group_data in parsed.items():
            res["access-group"][group] = res["access-group"].get(group, [])

            # scope section
            for permission, perm_data in group_data.items():
                if permission == "description":
                    continue
                if permission not in res["access-group"][group]:
                    res["access-group"][group].append(permission)

                    # list means read permission for all functions
                for scope, scope_data in perm_data.items():
                    res[scope] = res.get(scope, {})
                    if isinstance(scope_data, list):
                        for obj in scope_data:
                            res[scope][obj] = res[scope].get(obj, [])
                            if permission not in res[scope][obj]:
                                res[scope][obj].append(permission)
                    else:
                        for obj, obj_data in scope_data.items():
                            res[scope][obj] = res[scope].get(obj, [])
                            for perm in obj_data:
                                if perm not in res[scope][obj]:
                                    res[scope][obj].append(perm)

    return res


@ubus_connected
def create_session(
    timeout: typing.Optional[int] = None, dir: pathlib.Path = DEFAULT_ACL_DIR
) -> str:
    """Create a session which can be used to access Luci

    Returns session_id which can be used in sysauth cookie
    """
    import ubus

    args = {"timeout": timeout} if timeout else {}
    res = ubus.call("session", "create", args)

    session_id = res[0]["ubus_rpc_session"]

    acls = prepare_acls(dir)

    for scope, scope_data in acls.items():
        objects = []
        for obj, functions in scope_data.items():
            for function in functions:
                objects.append([obj, function])

        ubus.call(
            "session",
            "grant",
            {"ubus_rpc_session": session_id, "scope": scope, "objects": objects},
        )

    token = secrets.token_hex(16)
    # set token (probably used as CSRF token) and username
    ubus.call(
        "session",
        "set",
        {
            "ubus_rpc_session": session_id,
            "values": {"token": token, "username": "root"},
        },
    )

    return session_id


@ubus_connected
def touch_session(session_id: str) -> typing.Optional[int]:
    """Extends validity of session.

    Returns how log will session last (in seconds)
    """
    import ubus

    # this should refresh the session timeout
    try:
        res = ubus.call("session", "list", {"ubus_rpc_session": session_id})
    except RuntimeError:
        # error occured or session not found
        return None

    return res[0]["expires"]


@ubus_connected
def destroy_session(session_id: str) -> bool:
    """Destroys Luci's session

    Returns True if session was found or False if it was already expired
    """
    import ubus

    try:
        ubus.call("session", "destroy", {"ubus_rpc_session": session_id})
    except RuntimeError:
        # error occured or session not found
        return False
    return True
