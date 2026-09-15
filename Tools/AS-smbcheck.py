#!/usr/bin/env python3


from __future__ import annotations

import argparse
import getpass
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass


def print_banner() -> None:
	red = "\033[1;91m"
	yellow = "\033[1;93m"
	reset = "\033[0m"
	banner = r"""
============================================
                ASPIRATION
   ___  ____        ____  __  __ ____  ____
  / _ |/ __/_______/ __/ / / / // __ \/ __/
 / __ / _// __/___/\ \  / /_/ // /_/ /\ \
/_/ |_/___/_/      /___/  \____/ \____/___/
                 Mr-Loser
                ==========
"""
	print(f"{red}{banner}{yellow}          FIREWALL SHARE CHECK{reset}\n")


@dataclass
class Credentials:
	username: str
	password: str | None = None
	domain: str | None = None
	no_password: bool = False


def choose_mode() -> str:
	print("Authentication mode:")
	print("  1) Anonymous")
	print("  2) Guest")
	print("  3) Authenticated")
	while True:
		choice = input("Select [1-3]: ").strip()
		if choice in {"1", "2", "3"}:
			return {"1": "anonymous", "2": "guest", "3": "authenticated"}[choice]
		print("Please choose 1, 2, or 3.")


def prompt_credentials(mode: str) -> Credentials:
	if mode == "anonymous":
		return Credentials(username="", no_password=True)
	if mode == "guest":
		return Credentials(username="guest", no_password=True)

	username = input("Username: ").strip()
	if not username:
		raise ValueError("username cannot be empty")
	domain = input("Domain/workgroup (optional): ").strip() or None
	password = getpass.getpass("Password: ")
	return Credentials(username=username, password=password, domain=domain)


def authentication_file(credentials: Credentials) -> tempfile.NamedTemporaryFile:
	file = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False)
	os.chmod(file.name, 0o600)
	file.write(f"username = {credentials.username}\n")
	file.write(f"password = {credentials.password or ''}\n")
	if credentials.domain:
		file.write(f"domain = {credentials.domain}\n")
	file.close()
	return file


def run_smbclient(host: str, credentials: Credentials, share: str | None = None) -> int:
	auth_file = authentication_file(credentials)
	try:
		if share:
			service = f"//{host}/{share}"
			command = ["smbclient", service, "-A", auth_file.name]
		else:
			command = ["smbclient", "-L", host, "-A", auth_file.name]
		return subprocess.run(command).returncode
	finally:
		os.unlink(auth_file.name)


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		description="List and optionally connect to SMB shares on an authorized host."
	)
	parser.add_argument("host", nargs="?", help="SMB hostname or IP address")
	parser.add_argument(
		"-m",
		"--mode",
		choices=("anonymous", "guest", "authenticated"),
		help="authentication mode; omit it to choose interactively",
	)
	return parser


def main() -> int:
	if shutil.which("smbclient") is None:
		print("Error: smbclient is not installed or not in PATH.", file=sys.stderr)
		return 1

	print_banner()
	args = build_parser().parse_args()
	host = args.host or input("SMB host/IP: ").strip()
	if not host:
		print("Error: host cannot be empty.", file=sys.stderr)
		return 2

	mode = args.mode or choose_mode()
	try:
		credentials = prompt_credentials(mode)
	except (EOFError, KeyboardInterrupt):
		print("\nCancelled.", file=sys.stderr)
		return 130
	except ValueError as error:
		print(f"Error: {error}", file=sys.stderr)
		return 2

	print(f"\nListing SMB shares on {host}...")
	try:
		result = run_smbclient(host, credentials)
	except (OSError, KeyboardInterrupt) as error:
		print(f"SMB check failed: {error}", file=sys.stderr)
		return 1
	if result != 0:
		print("Could not list shares. Check the host and selected credentials.", file=sys.stderr)
		return result

	try:
		connect = input("\nConnect to a share? Enter its name, or press Enter to exit: ").strip()
	except (EOFError, KeyboardInterrupt):
		print()
		return 0
	if connect:
		if "/" in connect or "\\" in connect or connect in {".", ".."}:
			print("Invalid share name.", file=sys.stderr)
			return 2
		print(f"Opening //{host}/{connect}. Type 'help' for SMB commands.")
		return run_smbclient(host, credentials, connect)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
