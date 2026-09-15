#!/usr/bin/env python3
"""AS-scanner"""

from __future__ import annotations

import argparse
import concurrent.futures
import socket
import sys
from typing import Iterable


def print_banner() -> None:
	red = "\033[91m"
	reset = "\033[0m"
	banner = r"""
  
 ==================ASPIRATION====================
   ___  ____        ____
  / _ |/ __/_______/ __/______ ____  ___ ____
 / __ / _// __/___/\ \/ __/ _ `/ _ \/ -_) __/
/_/ |_/___/_/      /___/\__/\_,_/ .__/\__/_/
                               /_/
                     Mr-Loser
                 ----------------                       
"""
	print(f"{red}{banner}{reset}")


def parse_ports(value: str) -> list[int]:
	"""Parse ports like ``22,80,443,8000-8010`` or ``-`` for all ports."""
	if value.strip() == "-":
		return list(range(1, 65536))

	ports: set[int] = set()

	for item in value.split(","):
		item = item.strip()
		if not item:
			continue
		if "-" in item:
			start_text, end_text = item.split("-", 1)
			try:
				start, end = int(start_text), int(end_text)
			except ValueError as error:
				raise argparse.ArgumentTypeError(
					f"invalid port range: {item}"
				) from error
			if start > end:
				start, end = end, start
			ports.update(range(start, end + 1))
		else:
			try:
				ports.add(int(item))
			except ValueError as error:
				raise argparse.ArgumentTypeError(f"invalid port: {item}") from error

	invalid = sorted(port for port in ports if not 1 <= port <= 65535)
	if invalid:
		raise argparse.ArgumentTypeError(
			f"ports must be between 1 and 65535: {invalid[0]}"
		)
	if not ports:
		raise argparse.ArgumentTypeError("at least one port is required")
	return sorted(ports)


def scan_port(host: str, port: int, timeout: float) -> tuple[int, bool]:
	"""Return whether a TCP connection can be established to a port."""
	try:
		with socket.create_connection((host, port), timeout=timeout):
			return port, True
	except (ConnectionRefusedError, socket.timeout, TimeoutError, OSError):
		return port, False


def scan(host: str, ports: Iterable[int], timeout: float, workers: int) -> list[int]:
	"""Scan ports concurrently and return open ports in ascending order."""
	with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
		checks = [executor.submit(scan_port, host, port, timeout) for port in ports]
		open_ports = [
			port
			for check in concurrent.futures.as_completed(checks)
			for port, is_open in [check.result()]
			if is_open
		]
	return sorted(open_ports)


def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="Scan TCP ports on a host.")
	parser.add_argument("host", help="hostname or IP address to scan")
	parser.add_argument(
		"-p",
		"--ports",
		default="1-1024",
		help="ports to scan, e.g. 22,80,443, 1-1024, or - for all ports (default: 1-1024)",
	)
	parser.add_argument(
		"-t",
		"--timeout",
		type=float,
		default=0.5,
		help="connection timeout in seconds (default: 0.5)",
	)
	parser.add_argument(
		"-w",
		"--workers",
		type=int,
		default=100,
		help="maximum simultaneous connections (default: 100)",
	)
	return parser


def main() -> int:
	parser = build_parser()
	args = parser.parse_args()

	if args.timeout <= 0:
		parser.error("--timeout must be greater than zero")
	if args.workers <= 0:
		parser.error("--workers must be greater than zero")
	try:
		ports = parse_ports(args.ports)
		socket.getaddrinfo(args.host, None)
	except (argparse.ArgumentTypeError, socket.gaierror) as error:
		parser.error(str(error))

	print_banner()
	print(f"Scanning {args.host} ({len(ports)} TCP ports)...")
	try:
		open_ports = scan(args.host, ports, args.timeout, args.workers)
	except KeyboardInterrupt:
		print("\nScan interrupted.", file=sys.stderr)
		return 130

	if open_ports:
		print("Open ports:")
		for port in open_ports:
			try:
				service = socket.getservbyport(port, "tcp")
			except OSError:
				service = "unknown"
			print(f"  {port}/tcp ({service})")
	else:
		print("No open TCP ports found.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
