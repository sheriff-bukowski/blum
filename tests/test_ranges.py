from ipaddress import IPv4Address

import pytest

from blum.ranges import iter_ip_range, parse_ip_range


def test_parse_ip_range() -> None:
    start, end = parse_ip_range("192.168.1.1-192.168.1.3")
    assert start == IPv4Address("192.168.1.1")
    assert end == IPv4Address("192.168.1.3")


def test_parse_ip_range_rejects_reverse_range() -> None:
    with pytest.raises(ValueError):
        parse_ip_range("192.168.1.10-192.168.1.1")


def test_iter_ip_range_is_inclusive() -> None:
    result = list(
        iter_ip_range(
            IPv4Address("10.0.0.1"),
            IPv4Address("10.0.0.3"),
        )
    )
    assert result == [
        IPv4Address("10.0.0.1"),
        IPv4Address("10.0.0.2"),
        IPv4Address("10.0.0.3"),
    ]
