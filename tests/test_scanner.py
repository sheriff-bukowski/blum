from ipaddress import IPv4Address
from unittest.mock import patch

from blum.scanner import scan_range


def test_scan_range_defaults_interface_at_scan_level() -> None:
    start = IPv4Address("192.0.2.1")
    end = IPv4Address("192.0.2.1")

    with (
        patch("blum.scanner.resolve_interface", return_value="test0") as resolver,
        patch("blum.scanner._scan_batch", return_value=set()),
    ):
        result = scan_range(start, end, iface=None, verbose=False)

    resolver.assert_called_once_with(None, start)
    assert result == []
