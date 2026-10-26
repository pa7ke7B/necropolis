"""Tool registry. A minion may only call tools listed in its recipe, and every
call is routed through the binding circle before it lands here.

Each entry: name -> {fn, active, describes how to build an Action}.
To add a tool (nmap, nuclei, sqlmap, a hash-enrichment API...), write a plain
function elsewhere and register it here with active=True/False.
"""
from __future__ import annotations

from .recon import port_check

TOOLS = {
    "port_check": {
        "fn": port_check,
        "active": True,
        "help": "TCP-connect check of one port on an in-scope target.",
    },
}


def get(name: str):
    if name not in TOOLS:
        raise KeyError(f"no such tool: {name}")
    return TOOLS[name]
