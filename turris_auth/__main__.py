# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright 2021, CZ.NIC z.s.p.o. (http://www.nic.cz/)
import argparse
import getpass
import sys

from . import password


def input_password() -> str:
    """Request password from user through terminal."""
    while True:
        password1 = getpass.getpass("New password (input not printed!): ")
        password2 = getpass.getpass("New password again: ")
        if password1 == password2:
            return password1
        print("Passwords do not match! Please try again.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Set turris authentication")
    parser.add_argument(
        "--password",
        help="Set given password for authentication (this is insecure and passing password trough STDIN is more secure)",
    )
    args = parser.parse_args()

    new_password = args.password or input_password()
    password.assign(new_password)
    sys.exit(0)


if __name__ == "__main__":
    main()
