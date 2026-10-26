"""The minion runtime: the agent loop.

think (brain.decide) -> act (through the binding circle) -> record (phylactery),
until the goal is met, the essence runs out, or the lifespan expires. Then the
minion crumbles. Nothing it did escaped the circle; everything it learned is in
the phylactery.
"""
from __future__ import annotations

from . import tools
from .binding_circle import Action, BindingCircle, BindingError
from .grimoire import Recipe
from .phylactery import Finding, Phylactery


class Minion:
    def __init__(self, recipe: Recipe, brain, circle: BindingCircle, phylactery: Phylactery):
        self.recipe = recipe
        self.brain = brain
        self.circle = circle
        self.phylactery = phylactery
        self.history: list[dict] = []

    def command(self, goal: str, scope: dict) -> str:
        name = self.recipe.name
        self.phylactery.grant_essence(name, self.recipe.essence)
        print(f"~ raised {name} ({self.recipe.court} court) — essence {self.recipe.essence}")

        spent = 0
        for _ in range(self.recipe.lifespan):
            if spent >= self.recipe.essence:
                print(f"~ {name} is out of essence and crumbles.")
                break

            action = self.brain.decide(goal, scope, self.history)
            if action.get("tool") == "done":
                summary = action.get("summary", "done")
                self.phylactery.record(Finding(name, None, "summary", summary))
                print(f"~ {name}: {summary}")
                break

            tool_name = action["tool"]
            if tool_name not in self.recipe.tools:
                print(f"~ {name} reached for {tool_name}, not in its recipe. Skipped.")
                self.history.append(action)
                continue

            meta = tools.get(tool_name)
            try:
                self.circle.authorize(Action(
                    tool=tool_name,
                    target=action.get("target"),
                    port=action.get("port"),
                    active=meta["active"],
                ))
            except BindingError as e:
                print(f"~ binding circle: {e}")
                self.phylactery.record(Finding(
                    name, action.get("target"), "refused", str(e)))
                self.history.append(action)
                continue

            result = meta["fn"](
                action["target"],
                action["port"],
            ) if tool_name == "port_check" else meta["fn"](**{
                k: v for k, v in action.items() if k != "tool"})

            spent += 1
            self.phylactery.spend(name, 1)
            self.history.append(action)

            detail = str(result)
            self.phylactery.record(Finding(
                name, action.get("target"), tool_name, detail))
            if result.get("state") == "open":
                print(f"  + {action['target']}:{action['port']} open")

        return f"{name} spent {spent}/{self.recipe.essence} essence"
