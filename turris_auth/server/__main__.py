# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
import argparse
import logging
import logging.handlers
import os
import sys

from distutils.util import strtobool

from . import Server
from .config import config


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
