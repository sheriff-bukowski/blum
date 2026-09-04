# BlUM

BlUM is a lightweight Python ICMP IPv4 host discovery scanner built with Scapy.

> **Project note**
>
> This Python version of BlUM is an AI-assisted adaptation of an older C# BlUM
> project. The original implementation used SharpPcap/raw sockets and served as
> the basis for the CLI, IP-range scanning workflow, interface selection, and
> host-discovery behavior in this rewrite. The Python version restructures the
> project as an installable package, uses Scapy, adds type hints, exposes a
> programmatic API, and modernizes the packaging and command-line experience.

It supports both:

```bash
python -m blum
```

and, after installation:

```bash
blum
```

When `-i` / `--interface` is omitted, interface selection is performed inside
`scan_range(...)`. BlUM asks the routing table which interface should be used
to reach the first address in the requested range, then falls back to Scapy's
default interface if needed.

## Features

- ICMP Echo-based IPv4 host discovery
- Automatic default-route interface selection
- Explicit interface selection by name or index
- `python -m blum` support
- Installed `blum` console command
- Lazy IPv4 range generation
- Batched scanning
- Optional text output
- Type hints throughout
- Windows and Linux privilege checks
- MIT licensed

## Requirements

- Python 3.10+
- Administrator/root privileges for raw packet operations
- Scapy
- On Windows, Npcap may be required

## Installation

Use:

```bash
pip install blum
```
Or do it manually by clonning the repository:

```bash
git clone https://github.com/sheriff-bukowski/blum.git
cd blum
python -m pip install .
```

After installation:

```bash
python -m blum --help
blum --help
```

The `blum` command is installed as a standard Python console script. If your
Python Scripts/bin directory is not already on `PATH`, use `python -m blum` or
add that directory to `PATH`.

Because the package directory is at repository root, `python -m blum` also
works directly from the checkout once dependencies are installed.

## Usage

```text
usage: blum [-h] [-I] [-i INTERFACE] [-oN FILE]
            [--timeout TIMEOUT] [--batch-size BATCH_SIZE] [range]
```

Range format:

```text
START_IP-END_IP
```

Basic scan:

```bash
blum 192.168.1.1-192.168.1.254
```

Equivalent:

```bash
python -m blum 192.168.1.1-192.168.1.254
```

## Automatic interface selection

Usually you can omit `-i`:

```bash
blum 192.168.1.1-192.168.1.254
```

The defaulting happens inside `scan_range(...)`, so library users get the same
behavior:

```python
from ipaddress import IPv4Address

from blum import scan_range

hosts = scan_range(
    IPv4Address("192.168.1.1"),
    IPv4Address("192.168.1.254"),
)
```

Override it explicitly:

```python
hosts = scan_range(
    IPv4Address("192.168.1.1"),
    IPv4Address("192.168.1.254"),
    iface="Ethernet",
)
```

## Python API

`scan_range` is exposed directly from the top-level `blum` package:

```python
from ipaddress import IPv4Address

from blum import scan_range

hosts = scan_range(
    IPv4Address("192.168.1.1"),
    IPv4Address("192.168.1.254"),
)

for host in hosts:
    print(host)
```

You can still import it from its implementation module if preferred:

```python
from blum.scanner import scan_range
```

The interface argument is optional. If omitted, interface selection happens
inside `scan_range(...)` using the system route toward the first address in the
range:

```python
hosts = scan_range(
    IPv4Address("192.168.1.1"),
    IPv4Address("192.168.1.254"),
    iface=None,
)
```

To force an interface:

```python
hosts = scan_range(
    IPv4Address("192.168.1.1"),
    IPv4Address("192.168.1.254"),
    iface="Ethernet",
)
```

## List interfaces

```bash
blum -I
```

## Select an interface

By name:

```bash
blum -i "Ethernet" 192.168.1.1-192.168.1.254
```

By index:

```bash
blum -i 0 192.168.1.1-192.168.1.254
```

## Save results

```bash
blum -oN hosts.txt 192.168.1.1-192.168.1.254
```

## Tuning

Response timeout:

```bash
blum --timeout 3.0 192.168.1.1-192.168.1.254
```

Batch size:

```bash
blum --batch-size 128 192.168.1.1-192.168.1.254
```

## Windows

Install Npcap if required, open a terminal as Administrator, then:

```powershell
python -m pip install .
blum 192.168.1.1-192.168.1.254
```

## Linux

```bash
python3 -m pip install .
sudo blum 192.168.1.1-192.168.1.254
```

or:

```bash
sudo python3 -m blum 192.168.1.1-192.168.1.254
```

## Development

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
```

## Repository layout

```text
blum/
├── blum/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── interfaces.py
│   ├── ranges.py
│   └── scanner.py
├── tests/
│   ├── test_ranges.py
│   └── test_scanner.py
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements-dev.txt
├── requirements.txt
└── SECURITY.md
```

## Notes

ICMP discovery cannot prove that a non-responsive host is offline. Firewalls,
host policies, filtering, routing, or packet loss can prevent Echo Replies.

## Responsible use

Only scan systems and networks you own or have explicit permission to test.

## License

BlUM is open source under the [MIT License](LICENSE).
