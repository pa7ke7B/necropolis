"""Safe recon primitive: a TCP-connect port check. No nmap dependency.

This is an *active* action (it reaches out to the target), so it only ever runs
after the binding circle has authorized it. Wrap nmap/nuclei/etc. the same way:
a plain function that takes a target and returns a dict, registered in __init__.
"""
from __future__ import annotations

import socket


def port_check(target: str, port: int, timeout: float = 1.0) -> dict:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((target, port))
        return {"target": target, "port": port, "state": "open"}
    except (socket.timeout, ConnectionRefusedError, OSError):
        return {"target": target, "port": port, "state": "closed"}
    finally:
        sock.close()
