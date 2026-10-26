"""The altar — the necromancer's command line.

    raise <recipe> --goal "..."   raise a minion and set it on a goal
    scry                          read what the minions have learned
    banish                        wipe the phylactery (findings + ledger)
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys

import yaml

from .lich import Lich


def _load_config(path: str) -> dict:
    with open(path) as fh:
        return yaml.safe_load(fh)


def cmd_raise(args, config):
    lich = Lich(config)
    try:
        summary = lich.raise_minion(
            args.recipe,
            goal=args.goal,
            brain_kind=args.brain,
            auto_approve=args.auto_approve,
        )
        print(f"~ {summary}")
    finally:
        lich.close()


def cmd_scry(args, config):
    from .phylactery import Phylactery
    p = Phylactery(config["phylactery"]["path"])
    rows = p.findings()
    if not rows:
        print("The crypt is silent. No findings yet.")
        return
    for r in rows:
        when = dt.datetime.fromtimestamp(r["ts"]).strftime("%H:%M:%S")
        target = r["target"] or "-"
        print(f"[{when}] {r['minion']:<14} {r['kind']:<8} {target:<16} {r['detail']}")
    p.close()


def cmd_banish(args, config):
    from .phylactery import Phylactery
    p = Phylactery(config["phylactery"]["path"])
    p.banish_all()
    p.close()
    print("~ the phylactery is emptied. The dead rest.")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="necropolis", description="Command the undead.")
    parser.add_argument("--config", default="config.yaml")
    sub = parser.add_subparsers(dest="command", required=True)

    pr = sub.add_parser("raise", help="raise a minion and command it")
    pr.add_argument("recipe")
    pr.add_argument("--goal", required=True)
    pr.add_argument("--brain", choices=["offline", "anthropic"], default="offline")
    pr.add_argument("--auto-approve", action="store_true",
                    help="approve active actions automatically (lab only)")
    pr.set_defaults(func=cmd_raise)

    ps = sub.add_parser("scry", help="read the phylactery")
    ps.set_defaults(func=cmd_scry)

    pb = sub.add_parser("banish", help="wipe the phylactery")
    pb.set_defaults(func=cmd_banish)

    args = parser.parse_args(argv)
    config = _load_config(args.config)
    args.func(args, config)


if __name__ == "__main__":
    sys.exit(main())
