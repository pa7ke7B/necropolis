# Build Log

A running journal of work on Necropolis — what was done, what broke, what fixed
it, and what was learned. Newest entries at the top. This is both a progress
tracker and the raw material for writing this project up later.

---

## 2026-10-25 — Phase 0: telemetry foundation (COMPLETE)

**Goal:** get one victim's telemetry flowing into a SIEM and prove an attack is
visible end to end, all on a single MacBook Pro (M5 Pro, 24 GB, Apple Silicon).

### What was built
- **Runtime:** OrbStack (Apple-Silicon-native container + VM engine).
- **SIEM:** Wazuh single-node v4.14.9 (indexer + manager + dashboard) in Docker,
  indexer heap tuned to 1 GB to fit 24 GB of RAM.
- **Victim:** an OrbStack Ubuntu VM with the Wazuh agent (ARM64) enrolled and
  reporting.
- **First attack:** an SSH brute force (invalid-user failed logins) — ATT&CK
  **T1110** — generated with `sshpass`.

### Result
Attack captured and auto-tagged. Wazuh showed ~21 authentication failures on
`victim`, a level-10 SSH brute-force correlation, and MITRE tags for Password
Guessing / Brute Force / SSH under the Credential Access tactic. **Phase 0 done.**

### Gotchas solved (worth remembering)
- **`vm.max_map_count`** — the Wazuh indexer needs it raised inside OrbStack's
  Linux VM, not macOS. Set with a one-shot privileged container:
  `docker run --rm --privileged alpine sysctl -w vm.max_map_count=262144`.
- **Cert generation failure** — the cert tool set the SSL output directory
  read-only *before* copying `root-ca-manager.pem`/`.key`, so those two were
  missing and the manager/dashboard wouldn't start (bind-mount error). Fix:
  `chmod u+w` the dir, then manually copy `root-ca.pem`→`root-ca-manager.pem`
  and `root-ca.key`→`root-ca-manager.key` (they're the same CA in single-node).
- **Agent networking** — the OrbStack victim VM reaches the manager via the
  container's Docker-network IP; verified reachability with `nc -zv <ip> 1514/1515`
  before enrolling.
- **No auth log by default** — the minimal Ubuntu image lacked an SSH server and
  classic auth logging. Installed `openssh-server` + `rsyslog` so `/var/log/auth.log`
  exists and `wazuh-logcollector` can read it; restarted the agent afterward.

### Learned
- Wazuh is three cooperating services communicating over mutual TLS — a missing
  cert = a service that won't start (security by default).
- The manager self-monitors as node `000`; "no agents registered" refers only to
  external endpoints.
- "Alerts" ≠ "threats": ~5,000 total events, only ~21 meaningful. Signal-vs-noise
  is the core detection-engineering problem — and the job the AI layer will take on.
- Rule levels: SSH brute force tops out at level 10 by default, so 0 events at
  "level 12+" is expected, not a miss.

### Next
Phase 1 — install Atomic Red Team on the victim and run catalogued, ATT&CK-mapped
techniques systematically to start building coverage across the matrix.
