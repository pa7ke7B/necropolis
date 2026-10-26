"""The binding circle — the single chokepoint every tool call passes through.

Two jobs:
  1. Scope. A minion may only touch targets on the allowlist. No exceptions.
  2. Approval. Active actions (anything that reaches out and touches a target)
     are gated by policy: prompt the necromancer, deny outright, or auto-approve.

There is deliberately no way to reach a tool without an Authorization from here.
"""
from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass


class BindingError(Exception):
    """Raised when the circle refuses an action."""


@dataclass
class Action:
    tool: str
    target: str | None = None
    port: int | None = None
    active: bool = True        # does it reach out and touch the target?
    note: str = ""


class BindingCircle:
    def __init__(self, scope: dict, policy: dict, approver=None):
        self._networks = [self._net(e) for e in scope.get("allow", [])]
        self._ports = set(scope.get("ports", []))
        self._policy = policy.get("active_actions", "prompt")
        # approver(action) -> bool. Defaults to a terminal prompt.
        self._approver = approver or _terminal_approver

    @staticmethod
    def _net(entry: str) -> ipaddress._BaseNetwork:
        # Bare IPs become /32 (or /128) networks; CIDRs pass through.
        return ipaddress.ip_network(entry, strict=False)

    def _resolve(self, target: str) -> ipaddress._BaseAddress:
        try:
            return ipaddress.ip_address(target)
        except ValueError:
            return ipaddress.ip_address(socket.gethostbyname(target))

    def in_scope(self, target: str) -> bool:
        try:
            ip = self._resolve(target)
        except (ValueError, socket.gaierror):
            return False
        return any(ip in net for net in self._networks)

    def authorize(self, action: Action) -> Action:
        """Return the action if permitted; raise BindingError otherwise."""
        if action.target is not None:
            if not self.in_scope(action.target):
                raise BindingError(
                    f"target {action.target} is out of scope. Refused."
                )
            if action.port is not None and self._ports and action.port not in self._ports:
                raise BindingError(
                    f"port {action.port} is not in the permitted set. Refused."
                )
        if action.active:
            if self._policy == "deny":
                raise BindingError("policy forbids active actions (dry run).")
            if self._policy == "prompt" and not self._approver(action):
                raise BindingError("necromancer withheld approval.")
            # "auto" falls through — approved.
        return action


def _terminal_approver(action: Action) -> bool:
    where = action.target or "?"
    port = f":{action.port}" if action.port is not None else ""
    ans = input(
        f"  [binding circle] approve {action.tool} against {where}{port}? [y/N] "
    )
    return ans.strip().lower() in ("y", "yes")
