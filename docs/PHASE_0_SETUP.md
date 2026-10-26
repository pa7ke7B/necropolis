# Phase 0 — Telemetry Foundation (Mac-only Setup)

**Hardware:** MacBook Pro, M5 Pro, 24 GB RAM. Everything runs on this one machine
— no extra hardware. Apple Silicon (ARM64), so everything below runs native.

**Goal:** get one victim's logs flowing into Wazuh and prove you can find an
attack in the telemetry by hand.

**Definition of done:**
- [ ] OrbStack installed; Wazuh running; dashboard loads.
- [ ] One Linux victim with the Wazuh agent enrolled and reporting.
- [ ] You generated an event by hand and found it in Wazuh.
- [ ] Sigma CLI installed on the Mac; converted one sample rule.

---

## Architecture (all on the Mac)

- **Runtime: OrbStack** — Apple-Silicon-native, far lighter on RAM than Docker
  Desktop. Gives you both a Docker engine (for the Wazuh stack) and cheap Linux
  VMs (for the victim).
- **SIEM: Wazuh single-node** — runs as ARM64 containers under OrbStack.
- **Victim: an OrbStack Ubuntu VM** — a real systemd host, so the Wazuh agent
  installs exactly as it would on any Linux box.
- **Attacker + control: the Mac itself** — for Phase 0–1 you generate the events
  on the victim directly; no separate Kali box needed yet.
- **Isolation:** keep the lab internal. Don't publish the victim's service ports
  to your home network. Tear the whole thing down when you're not using it.

**Memory budget (24 GB):** macOS + Cursor leave plenty if you tune the Wazuh
indexer's heap down (Step 2). Expect the Wazuh stack ~4–6 GB, victim ~0.5 GB.
Don't run large extra VMs at the same time and you're comfortable.

---

## Step 1 — Install OrbStack

Download from orbstack.dev (or `brew install orbstack`). Launch it once so the
Docker engine is running. Confirm:

```bash
docker version        # should talk to OrbStack's engine
```

---

## Step 2 — Stand up Wazuh (single-node, heap-tuned)

```bash
sudo sysctl -w vm.max_map_count=262144   # see the note below if the indexer fails

git clone https://github.com/wazuh/wazuh-docker.git -b <latest-stable-tag>
cd wazuh-docker/single-node
```

**Before bringing it up, tune the indexer heap** so it fits 24 GB. In
`docker-compose.yml`, find the `wazuh.indexer` service and set its heap to ~1 GB:

```yaml
    environment:
      - "OPENSEARCH_JAVA_OPTS=-Xms1g -Xmx1g"
```

Then:

```bash
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
```

- Dashboard: `https://localhost` — default `admin` / `SecretPassword`.
  **Change it immediately.**
- Exact version tag + any step changes: the official **Wazuh Docker single-node**
  guide at https://documentation.wazuh.com. Don't pin a tag from memory.

**`vm.max_map_count` note (the #1 gotcha on Mac):** this sysctl lives inside the
Linux VM that backs the container engine, not macOS. If the indexer container
won't stay up, this is almost always why — the value has to be set in that VM.
Bring me the error and I'll give you the exact OrbStack incantation for your
version.

---

## Step 3 — Create a victim and enroll the agent

```bash
orb create ubuntu victim      # a lightweight Ubuntu VM, runs in seconds
orb -m victim                 # shell into it
```

In the Wazuh dashboard, open **"Deploy new agent"**, pick Linux/DEB, and set the
manager address so the victim can reach it. The wizard prints the exact
install + enroll command — run it inside the `victim` shell. Start the agent; it
shows **active** under *Agents* within a minute.

**Networking point to get right:** the victim VM reaches the manager through the
ports the compose published on the Mac host. If the agent sits at "never
connected," it's a reachability problem between the VM and those host ports —
tell me and we'll fix the manager address.

---

## Step 4 — Generate an event and find it (the first win)

Inside the victim, create failed logins (ATT&CK **T1110, Brute Force**):

```bash
ssh nosuchuser@localhost      # wrong user; repeat 4-5 times
```

In the dashboard → the agent's **Threat Hunting / Security events** → filter for
authentication failures. You'll see them, already tagged with the MITRE
technique. That's Phase 0 working — you can see an attack in the telemetry.

---

## Step 5 — Install the Sigma toolchain (prep for Phase 2)

On the Mac:

```bash
pipx install sigma-cli        # or: brew install sigma-cli
sigma version
sigma list targets
```

Pull one rule from the public **SigmaHQ/sigma** repo and convert it, just to see
the toolchain run. Wiring conversion into Wazuh comes in Phase 2.

---

## Teardown (keep your daily driver clean)

```bash
cd wazuh-docker/single-node && docker compose down   # stop the SIEM
orb stop victim                                       # pause the victim
```

Nothing is installed on macOS itself — it all lives in OrbStack. Keep it that way.

---

## Next

**Phase 1:** install Atomic Red Team on the victim, run a few ATT&CK-mapped
tests, note each technique ID. Then Phase 2: find each test's telemetry and
hand-write the Sigma rule that catches it.

Windows victims (for broader ATT&CK coverage) would need x86 hardware you don't
have — skip them. Linux + web + the LLM-target work in Phase 5 give you a strong
project without Windows.
