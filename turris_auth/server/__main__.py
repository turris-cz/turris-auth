# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2025, CZ.NIC z.s.p.o. (http://www.nic.cz/)
import argparse
import logging
import logging.handlers
import os
import sys

from . import Server
from .config import config


def strtobool (val):
    """ Copied from depracated python module distutils

    Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def main():
    parser = argparse.ArgumentParser(description="Authentication server for Turris")
    parser.add_argument(
        "--lighttpd-config", action="store_true", help="Print Lighttpd configuration instead of running server"
    )
    parser.add_argument(
        "--report-passwords", action="store_true", help="Report invalid passwords in plain text in logs"
    )
    parser.add_argument(
        "--luci-login",
        action="store_true",
        default=bool(strtobool(os.environ.get("TURRIS_AUTH_LUCI", "false"))),
    )
    args = parser.parse_args()

    if args.lighttpd_config:
        print(config(args.luci_login))
        sys.exit(0)

    toplogger = logging.getLogger()
    toplogger.addHandler(logging.handlers.SysLogHandler("/dev/log"))
    toplogger.setLevel(logging.INFO)
    sys.exit(Server(args.report_passwords, args.luci_login).run())


if __name__ == "__main__":
    main()
