# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
"""Lighttpd authentication for Turris routers. This provides easy way to request authentication for web services running
on the router.
"""
from . import password

__all__ = ["password"]
