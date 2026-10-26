"""The Lich — the orchestrator. Takes your command, raises the right minion
from its recipe, wires it to the binding circle and the phylactery, and sets it
loose. For now it raises one minion per command; growing it into a planner that
decomposes a campaign into several minions is the natural next step.
"""
from __future__ import annotations

from . import grimoire
from .binding_circle import BindingCircle
from .brain import make_brain
from .minion import Minion
from .phylactery import Phylactery


class Lich:
    def __init__(self, config: dict):
        self.config = config
        self.phylactery = Phylactery(config["phylactery"]["path"])

    def raise_minion(self, recipe_name: str, goal: str, brain_kind: str = "offline",
                     auto_approve: bool = False) -> str:
        recipe = grimoire.load(recipe_name)

        policy = dict(self.config.get("policy", {}))
        if auto_approve:
            policy["active_actions"] = "auto"

        circle = BindingCircle(self.config["scope"], policy)
        brain = make_brain(brain_kind, prompt=recipe.prompt, model=recipe.model)
        minion = Minion(recipe, brain, circle, self.phylactery)
        return minion.command(goal, self.config["scope"])

    def close(self) -> None:
        self.phylactery.close()
