from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from ipaddress import IPv4Address
from pathlib import Path

from .interfaces import list_interfaces
from .ranges import parse_ip_range
from .scanner import scan_range


def is_admin() -> bool:
    """Return whether the process has elevated privileges."""
    if os.name == "nt":
        try:
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            return False

    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="blum",
        description="Lightweight ICMP IPv4 host discovery scanner.",
    )

    parser.add_argument(
        "-I",
        action="store_true",
        dest="show_interfaces",
        help="show available interfaces and exit",
    )

    parser.add_argument(
        "-i",
        "--interface",
        metavar="INTERFACE",
        default=None,
        help=(
            "interface name or index; if omitted, resolve the interface "
            "from the system route for the scan range"
        ),
    )

    parser.add_argument(
        "-oN",
        "--output",
        metavar="FILE",
        type=Path,
        default=None,
        help="write discovered hosts to a text file",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="response timeout in seconds (default: 2.0)",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=256,
        help="addresses per scan batch (default: 256)",
    )

    parser.add_argument(
        "range",
        nargs="?",
        help="IPv4 range in START_IP-END_IP form",
    )

    return parser


def write_results(path: Path, hosts: Sequence[IPv4Address]) -> None:
    """Write one discovered IPv4 address per line."""
    path.write_text(
        "".join(f"{host}\n" for host in hosts),
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser: argparse.ArgumentParser = build_parser()
    args: argparse.Namespace = parser.parse_args(argv)

    if args.show_interfaces:
        list_interfaces()
        return 0

    if args.range is None:
        parser.print_help()
        return 1

    try:
        start_ip, end_ip = parse_ip_range(args.range)
    except ValueError as exc:
        print(f"BlUM> Invalid IP range: {exc}")
        return 1

    if not is_admin():
        print("BlUM> Scans require administrator/root privileges to run.")
        return 1

    try:
        hosts: list[IPv4Address] = scan_range(
            start_ip,
            end_ip,
            iface=args.interface,
            timeout=args.timeout,
            batch_size=args.batch_size,
        )
    except ValueError as exc:
        print(f"BlUM> {exc}")
        return 1
    except PermissionError:
        print("BlUM> Permission denied. Run as Administrator/root.")
        return 1
    except KeyboardInterrupt:
        print("\nBlUM> Scan interrupted.")
        return 130
    except Exception as exc:
        print(f"\nBlUM> Scan error: {exc}")
        return 1

    print(f"BlUM> A total of {len(hosts)} hosts up found:")
    for host in hosts:
        print(f"BlUM> {host}")

    if args.output is not None:
        try:
            write_results(args.output, hosts)
        except OSError as exc:
            print(f"BlUM> Unable to write output file: {exc}")
            return 1

        print(f"BlUM> Results written to: {args.output}")

    return 0
