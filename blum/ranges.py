from __future__ import annotations

import ipaddress
from collections.abc import Iterator
from ipaddress import IPv4Address


def parse_ip_range(value: str) -> tuple[IPv4Address, IPv4Address]:
    """Parse a START_IP-END_IP IPv4 range."""
    parts: list[str] = value.split("-", maxsplit=1)

    if len(parts) != 2:
        raise ValueError("range must use START_IP-END_IP format")

    try:
        start = IPv4Address(parts[0].strip())
        end = IPv4Address(parts[1].strip())
    except ipaddress.AddressValueError as exc:
        raise ValueError("invalid IPv4 address") from exc

    if int(start) > int(end):
        raise ValueError("start IP must be lower than or equal to end IP")

    return start, end


def iter_ip_range(
    start: IPv4Address,
    end: IPv4Address,
) -> Iterator[IPv4Address]:
    """Yield an IPv4 range lazily."""
    current: int = int(start)
    last: int = int(end)

    while current <= last:
        yield IPv4Address(current)
        current += 1
