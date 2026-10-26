# Necropolis

**An AI-driven detection-engineering purple-loop platform.**

Necropolis raises specialized security agents ("minions") that emulate adversary
behavior against an isolated lab, measure whether existing detections catch it,
and use an LLM to draft the detections that close the gaps — with every action
routed through a least-privilege authorization layer so the whole thing is safe
to run and to share.

The AI agent layer is the differentiator; the headline is **detection coverage
you can measure.** It spans purple teaming, detection engineering, and AI
security (both securing the agents themselves and treating an LLM as an attack
target).

> ⚠️ **Lab use only.** Every offensive action is confined to targets the operator
> owns and has explicitly scoped. Necropolis orchestrates known, catalogued
> security tools — it does not author novel exploits or malware. See
> [Ethics & scope](#ethics--scope).

---

## Status

🟢 **Phase 0 complete** — telemetry foundation is live: Wazuh SIEM running, a
monitored victim, and a first attack (SSH brute force, ATT&CK T1110) captured
and auto-tagged end to end. See the [build log](docs/BUILD_LOG.md).

Working toward Phase 1 (adversary emulation with Atomic Red Team). Full plan in
the [build plan](docs/BUILD_PLAN.md).

---

## The loop

```
emulate (ATT&CK technique)  ->  observe telemetry (SIEM)  ->  check detections
      ^                                                             |
      |                                                             v
 validate & commit  <-  human review  <-  AI drafts detection  <-  gap found?
```

Each pass raises measured ATT&CK coverage. That delta — "coverage went from X to
Y, AI-assisted" — is the point.

---

## How it fits together

- **Lab (local, on the Mac via OrbStack):** Atomic Red Team emulates attacks on a
  victim VM; the victim's logs flow to a **Wazuh SIEM** that tags events with
  MITRE ATT&CK; Sigma detections live in a version-controlled repo.
- **Necropolis control plane (Python):** a CLI drives a **Lich** orchestrator
  that raises minions; every tool call passes through the **binding circle**
  (scope allowlist + human approval) before reaching the **tool layer** (MCP
  servers for Wazuh, Atomic Red Team, Sigma, git). State lives in the
  **phylactery** (SQLite).
- **Claude (the brain):** called for judgment — what to emulate, reading
  telemetry, drafting detections — never for direct action.

---

## Repository layout

```
necropolis/
├── README.md              # this file
├── docs/
│   ├── BUILD_PLAN.md      # phased roadmap, stack, frameworks, prereqs
│   ├── PHASE_0_SETUP.md   # Mac/OrbStack lab setup, step by step
│   └── BUILD_LOG.md       # running journal of work done
├── necropolis/            # the Python control-plane code (starter spine)
├── grimoire/              # minion recipes (YAML)
├── config.yaml            # scope + policy for the binding circle
└── docker-compose.yml     # the cursed graveyard (vulnerable targets)
```

---

## Quickstart

**The lab:** follow [docs/PHASE_0_SETUP.md](docs/PHASE_0_SETUP.md) to stand up
Wazuh and a victim under OrbStack.

**The control plane (starter spine, runs offline):**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m necropolis.cli raise gravekeeper --goal "inventory the graveyard" --auto-approve
python -m necropolis.cli scry
```

---

## Anchor frameworks

MITRE ATT&CK · MITRE ATLAS · Sigma · OWASP Top 10 for LLM Applications ·
Atomic Red Team.

---

## Ethics & scope

Lab use only. The binding circle enforces a scope allowlist and human-in-the-loop
approval for every active action — this is a deliberate design constraint, not an
afterthought. Necropolis orchestrates legitimate, catalogued security tooling; it
does not generate exploits or malware. Do not point any part of it at systems you
do not own and have explicit authorization to test.
