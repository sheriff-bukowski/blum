from __future__ import annotations

from ipaddress import IPv4Address
from typing import Any, TypeAlias

from scapy.all import conf, get_if_addr, get_if_list

Interface: TypeAlias = Any


def list_interfaces() -> None:
    """Print interfaces available to Scapy."""
    interfaces: list[str] = get_if_list()

    print("BlUM> INTERFACES:\n")

    for index, iface in enumerate(interfaces):
        try:
            address: str = get_if_addr(iface)
        except Exception:
            address = "None"

        print(f"<{index}> Interface: {iface}, IP Address: {address}")


def resolve_interface(
    requested_interface: str | None,
    destination: IPv4Address,
) -> Interface:
    """Resolve an explicit interface or the system default route interface."""
    interfaces: list[str] = get_if_list()

    if requested_interface is not None:
        value: str = requested_interface.strip()

        if value.isdigit():
            index: int = int(value)
            if not 0 <= index < len(interfaces):
                raise ValueError(f"interface index {index} is invalid")
            return interfaces[index]

        if value in interfaces:
            return value

        normalized: str = value.casefold()
        for iface in interfaces:
            if iface.casefold() == normalized:
                return iface

        raise ValueError(f"interface '{requested_interface}' was not found")

    try:
        route: tuple[Any, ...] = conf.route.route(str(destination))
        route_iface: Interface = route[0]
        if route_iface:
            return route_iface
    except Exception:
        pass

    if conf.iface:
        return conf.iface

    raise ValueError("unable to resolve the default network interface")
