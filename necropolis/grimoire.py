"""Load minion recipes from the grimoire."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import yaml


@dataclass
class Recipe:
    name: str
    court: str = "black"            # black (defense) | red (offense)
    model: str = "claude-sonnet-4-5"
    prompt: str = ""
    tools: list[str] = field(default_factory=list)
    essence: int = 8               # max tool calls before the minion crumbles
    lifespan: int = 12             # max reasoning iterations


def load(name: str, grimoire_dir: str = "grimoire") -> Recipe:
    path = os.path.join(grimoire_dir, f"{name}.yaml")
    with open(path) as fh:
        data = yaml.safe_load(fh) or {}
    data.setdefault("name", name)
    return Recipe(**data)
