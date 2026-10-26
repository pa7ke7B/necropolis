"""The brain decides a minion's next action, one step at a time.

Interface: decide(goal, scope, history) -> action dict.
  action is either {"tool": "<name>", "target": ..., "port": ...}
  or {"tool": "done", "summary": "..."}.

Two implementations:
  OfflineBrain   — deterministic, no API key, good for demos and tests.
  AnthropicBrain — asks Claude for the next action as strict JSON.
"""
from __future__ import annotations

import json
import os
import re

_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


class OfflineBrain:
    """Walks the in-scope ports of one target, then declares itself done.

    Target selection: an explicit IP in the goal wins (so an out-of-scope goal
    like "scan 8.8.8.8" is passed through and the circle gets to refuse it);
    otherwise the first concrete IP in scope.
    """

    def decide(self, goal: str, scope: dict, history: list[dict]) -> dict:
        target = self._target(goal, scope)
        done_ports = {h["port"] for h in history if h.get("tool") == "port_check"}
        for port in scope.get("ports", []):
            if port not in done_ports:
                return {"tool": "port_check", "target": target, "port": port}
        return {"tool": "done", "summary": f"swept {len(done_ports)} ports on {target}"}

    @staticmethod
    def _target(goal: str, scope: dict) -> str:
        m = _IPV4.search(goal)
        if m:
            return m.group(0)
        for entry in scope.get("allow", []):
            host = entry.split("/")[0]
            if _IPV4.fullmatch(host):
                return host
        return "127.0.0.1"


class AnthropicBrain:
    """Asks Claude for the next action. Needs ANTHROPIC_API_KEY."""

    def __init__(self, model: str = "claude-sonnet-4-5", prompt: str = ""):
        import anthropic  # imported lazily so offline runs need no install
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.model = model
        self.system = prompt or "You are a recon minion. Be precise and safe."

    def decide(self, goal: str, scope: dict, history: list[dict]) -> dict:
        user = (
            f"Goal: {goal}\n"
            f"Scope (you may ONLY touch these): {json.dumps(scope)}\n"
            f"Actions so far: {json.dumps(history)}\n\n"
            "Available tool: port_check(target, port).\n"
            'Reply with ONE JSON object and nothing else: '
            '{"tool":"port_check","target":"<ip>","port":<int>} '
            'or {"tool":"done","summary":"<text>"}.'
        )
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            system=self.system,
            messages=[{"role": "user", "content": user}],
        )
        text = "".join(b.text for b in msg.content if b.type == "text").strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return {"tool": "done", "summary": "brain returned no action"}
        return json.loads(match.group(0))


def make_brain(kind: str, prompt: str = "", model: str = "claude-sonnet-4-5"):
    if kind == "anthropic":
        return AnthropicBrain(model=model, prompt=prompt)
    return OfflineBrain()
