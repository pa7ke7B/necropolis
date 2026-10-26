# Necropolis — Build Plan

An AI-driven **detection-engineering purple-loop** platform. You raise
specialized security agents ("minions") that emulate adversary behavior against
an isolated lab, measure whether existing detections catch it, and use an LLM to
draft the detections that close the gaps — every action routed through a
least-privilege authorization layer (the "binding circle").

**Positioning:** a purple-team automation platform with detection engineering at
its core and AI *and* AI-security woven through. The AI agent layer is the
differentiator, not the headline — the headline is detection coverage you can
measure.

---

## The loop

```
emulate (ATT&CK technique)  ->  observe telemetry (SIEM)  ->  check detections
      ^                                                             |
      |                                                             v
 validate & commit  <-  human review  <-  AI drafts detection  <-  gap found?
```

Each pass through the loop raises measured ATT&CK coverage. That measurable
delta ("coverage went from X to Y techniques, AI-assisted") is the whole value
proposition — for the tool and for the resume.

---

## The two AI angles (keep them distinct)

1. **AI as the engine.** LLM agents read attack telemetry, cross-reference
   ATT&CK/ATLAS, and draft Sigma/YARA detections; reason about coverage gaps;
   triage findings. Flagship use: *detection synthesis* from telemetry.
2. **AI security.**
   - *Defensive (securing our own agents):* scope enforcement, approval gating,
     treating all LLM output as untrusted before it touches a tool. (OWASP Top 10
     for LLM Applications.)
   - *Offensive (LLM as a target):* add an AI app to the lab, emulate prompt
     injection / jailbreak / exfiltration, and build detections for those
     attacks. (MITRE ATLAS.) This is the rare, differentiated piece.

---

## Tech stack

### Dev environment
- **Cursor** — primary editor/agent (AI-native; already subscribed). Optionally
  run Claude Code in the terminal alongside for multi-file agentic work; it's
  MCP-native, which matters because the tool layer is MCP servers.
- **Python 3.12+**, managed with `uv`. `ruff` for lint, `pytest` for detection
  tests.
- **Git + GitHub**, with **GitHub Actions** CI running pytest + Sigma validation
  on every push. This CI *is* detection-as-code.

### Homelab
- **Proxmox** (type-1 hypervisor; snapshot/clone to reset compromised victims in
  seconds). Docker-on-one-box is an acceptable minimal start.
- **Hardware:** mini-PC/NUC or small tower, 32–64 GB RAM, ~1 TB SSD.
- **Topology — isolated lab network** (separate VLAN/vSwitch, no route to home
  LAN, controlled egress), three roles:
  - **Attacker** — Kali.
  - **Victim(s)** — OWASP Juice Shop, a vulnerable Linux box, later a Windows VM
    (with Sysmon) for Windows ATT&CK coverage, later an LLM app.
  - **Telemetry/SIEM** — see below.

### Integrations / components
- **SIEM: Wazuh** — open-source XDR/SIEM, free, Win/Linux agents, built-in MITRE
  ATT&CK mapping. (Elastic/OpenSearch + Kibana is the alternative stack.)
- **Telemetry:** Wazuh agents + Sysmon on Windows.
- **Detection: Sigma** + `pySigma`/`sigma-cli` to convert rules to the SIEM's
  query language.
- **Emulation: Atomic Red Team** (fast, ATT&CK-mapped), **MITRE Caldera**
  (automated campaigns) later.
- **AI: Anthropic API** (Claude) for generation/reasoning agents, wired through
  the MCP tool layer.
- **Threat intel (optional):** NVD / CISA KEV, VirusTotal.

### Hosting
- **Lab:** local, isolated, never internet-exposed.
- **Tool:** runs locally (CLI) now; only outbound traffic is HTTPS to the
  Anthropic API. Secrets in a gitignored `.env` or a secrets manager — never in
  the repo. Later: containerize (Docker), optionally co-locate on the SIEM box.
- **Public face = the GitHub repo + docs + a demo video**, not a live instance.
- **AI-security hygiene:** scrub/limit telemetry sent to the API; manage keys;
  control lab egress.

### How an end user uses it
1. Set scope, point the tool at the lab SIEM.
2. `raise` a campaign — emulate a technique against a victim.
3. Tool pulls the resulting telemetry and checks existing detections for a hit.
4. On a miss, the AI drafts a Sigma rule; the user reviews/edits/approves
   (human-in-the-loop).
5. Approved rule commits to the detection-as-code repo; CI validates it.
6. Coverage dashboard (ATT&CK Navigator-style heatmap) shows before vs after.

Interface: CLI first, then a web "crypt" dashboard for the coverage heatmap and
the rule-review queue. Ship as a `uv`/pip install or a Docker image.

---

## Phased roadmap

Each phase ships something runnable and teaches a named skill.

### Phase 0 — Telemetry foundation
The step everyone skips; it's the whole game. No detection engineering without
logs.
- [ ] Stand up the lab: one victim + a log pipeline + Sigma CLI.
- [ ] Deploy Wazuh; get a victim's logs flowing into it.
- [ ] Confirm you can find a specific action in the telemetry by hand.
- **Learn:** log sources, Sigma rule format, how an attack becomes telemetry.

### Phase 1 — Emulate (red)
- [ ] Install Atomic Red Team on a victim.
- [ ] Run 3–5 atomic tests; note the ATT&CK technique ID for each.
- [ ] (Later) explore Caldera for automated campaigns.
- **Learn:** MITRE ATT&CK, adversary emulation, Atomic Red Team.

### Phase 2 — Detect & measure
- [ ] For each atomic test, locate its telemetry and hand-write a Sigma rule.
- [ ] Confirm each rule fires on replay; tune false positives.
- [ ] Track coverage: techniques covered vs not (ATT&CK Navigator).
- **Learn:** detection engineering fundamentals, coverage mapping, tuning.

### Phase 3 — AI generation (the loop closes)
- [ ] Build the agent that reads telemetry from an undetected attack + ATT&CK
      context and drafts a Sigma rule.
- [ ] Human-in-the-loop review/approve, then commit to the detection repo.
- [ ] Measure the AI-assisted coverage delta.
- **Learn:** agent design, structured output, *evaluating* AI-generated rules.

### Phase 4 — Secure the tool (AI security, defensive)
- [ ] Harden the binding circle: scope allowlisting, approval gates.
- [ ] Treat all LLM output as untrusted before any tool call.
- [ ] Add budget/lifespan limits (blast-radius control).
- **Learn:** OWASP Top 10 for LLM Applications, prompt injection, least-privilege
  agent design.

### Phase 5 — LLM as target (AI security, offensive — the differentiator)
- [ ] Add an LLM app to the lab as a victim.
- [ ] Emulate attacks against it (prompt injection, jailbreak, exfiltration).
- [ ] Build detections for those attacks; map to MITRE ATLAS.
- **Learn:** MITRE ATLAS, AI red teaming, LLM attack detection.

---

## Prerequisites

**Already covered:** Python, log analysis, REST APIs, virtualization, and
security-ops fundamentals (SIEM logic, alerting, analyst workflow) transfer
directly.

**Learn just-in-time, per phase:** Sigma syntax (Phase 2), agent/LLM tool-use
patterns (Phase 3), Wazuh specifics (Phase 0).

**Genuinely new ground:** MITRE ATLAS + LLM security (Phase 5) — new for almost
everyone, which is why it's valuable.

**Worth one afternoon before starting:** get comfortable with how MITRE ATT&CK
is structured (tactics vs techniques, technique IDs) and read the anatomy of 2–3
Sigma rules. That's the only real prerequisite.

---

## Anchor frameworks

Orient everything around these five; learning them through this project covers
the modern purple-team + AI-security surface area:

- **MITRE ATT&CK** — adversary techniques (the backbone).
- **MITRE ATLAS** — ATT&CK for AI systems.
- **Sigma** — vendor-neutral detection rules.
- **OWASP Top 10 for LLM Applications** — securing the AI layer.
- **Atomic Red Team** — ATT&CK-mapped emulation.

---

## What this demonstrates (resume framing)

- Automated **adversary emulation + detection engineering** mapped to MITRE
  ATT&CK, auto-generating Sigma detections to measure and close coverage gaps.
- A **least-privilege authorization layer** enforcing scope allowlisting and
  human-in-the-loop approval for all active actions — zero-trust applied to
  automated tooling.
- **SOAR-style orchestration** integrating threat intel with automated
  enrichment and triage playbooks.
- **AI security** on both sides: hardening the agent system (OWASP LLM Top 10)
  and emulating/detecting attacks against LLMs (MITRE ATLAS).

The through-line: a security engineer who can *build* — agents plus the
governance around them.

---

## Ethics / scope

Lab use only. Every offensive action is confined to targets you own and have
explicitly scoped. The authorization layer exists specifically to make this safe
and legal to run and to share. The tool orchestrates known, catalogued security
tools — it does not author novel exploits or malware.
