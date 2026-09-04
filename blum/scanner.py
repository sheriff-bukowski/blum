from __future__ import annotations

from collections.abc import Sequence
from ipaddress import IPv4Address
from typing import Any

from scapy.all import ICMP, IP, sr

from .interfaces import Interface, resolve_interface
from .ranges import iter_ip_range

DEFAULT_TIMEOUT: float = 2.0
DEFAULT_INTER_PACKET_DELAY: float = 0.005
DEFAULT_BATCH_SIZE: int = 256


def _scan_batch(
    addresses: Sequence[IPv4Address],
    iface: Interface,
    *,
    timeout: float,
    inter_packet_delay: float,
) -> set[IPv4Address]:
    """Scan one batch and return hosts that sent ICMP Echo Replies."""
    if not addresses:
        return set()

    packets: list[Any] = [
        IP(dst=str(address)) / ICMP()
        for address in addresses
    ]

    answered, _ = sr(
        packets,
        iface=iface,
        timeout=timeout,
        inter=inter_packet_delay,
        retry=0,
        verbose=0,
    )

    hosts: set[IPv4Address] = set()

    for _, response in answered:
        if not response.haslayer(IP) or not response.haslayer(ICMP):
            continue

        icmp = response.getlayer(ICMP)
        if int(icmp.type) != 0:
            continue

        hosts.add(IPv4Address(response[IP].src))

    return hosts


def scan_range(
    start: IPv4Address,
    end: IPv4Address,
    iface: str | None = None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    inter_packet_delay: float = DEFAULT_INTER_PACKET_DELAY,
    batch_size: int = DEFAULT_BATCH_SIZE,
    verbose: bool = True,
) -> list[IPv4Address]:
    """Discover hosts in an inclusive IPv4 range.

    Interface defaulting happens here. If ``iface`` is None, BlUM resolves
    the route-selected interface for ``start`` and falls back to Scapy's
    configured default interface.
    """
    if int(start) > int(end):
        raise ValueError("start IP must be lower than or equal to end IP")
    if timeout <= 0:
        raise ValueError("timeout must be greater than zero")
    if inter_packet_delay < 0:
        raise ValueError("inter_packet_delay cannot be negative")
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    resolved_iface: Interface = resolve_interface(iface, start)
    total: int = int(end) - int(start) + 1

    if verbose:
        print(f"BlUM> Preparing to scan range {start} to {end}...")
        print(f"BlUM> Using interface: {resolved_iface}")
        print(f"BlUM> Total addresses: {total}")
        print("BlUM> Starting packet sending!")

    hosts_up: set[IPv4Address] = set()
    batch: list[IPv4Address] = []
    scanned: int = 0

    def process_batch(address_batch: list[IPv4Address]) -> None:
        nonlocal scanned
        hosts_up.update(
            _scan_batch(
                address_batch,
                resolved_iface,
                timeout=timeout,
                inter_packet_delay=inter_packet_delay,
            )
        )
        scanned += len(address_batch)

        if verbose:
            print(
                f"\rBlUM> Scanned {scanned} out of {total} addresses...",
                end="",
                flush=True,
            )

    for address in iter_ip_range(start, end):
        batch.append(address)

        if len(batch) >= batch_size:
            process_batch(batch)
            batch.clear()

    if batch:
        process_batch(batch)

    if verbose:
        print()
        print("BlUM> Packet sending finished! Preparing results...")

    return sorted(hosts_up, key=int)
