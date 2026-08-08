# Agent Integrity Skills

Portable **SKILL.md** packs for **Grok Build**, **Claude Code**, **Codex**, **Cursor**, and similar agents.

**Core idea:** keep agents useful for long stretches of work **without** letting them silently approve high-stakes mistakes.

Two skills form the **general toolkit** (any domain). Two more are **optional** (promotion language + investing).

---

## The general toolkit (use anywhere)

### 1. `dual-agent-review` — quality & permission

| | |
|--|--|
| **Question it answers** | “Is this plan/diff/claim safe enough to **proceed**?” |
| **Works for** | Code, product design, ops runbooks, research, hiring scorecards, security changes — **not only investing** |
| **Output** | Exactly one of: **ACCEPT** · **REVISE** · **HUMAN_REQUIRED** |
| **Key rules** | Hostile review; at most **one** REVISE round; **HUMAN_REQUIRED cannot self-clear**; same-model QA ≠ full independence for freezes/money/production |
| **Call** | `/dual-agent-review` (Grok) or “use dual-agent-review on this artefact” |

**Why it exists:** One agent writing *and* rubber-stamping itself is how bad merges, bad deploys, and fake “we’re ready” claims happen.

---

### 2. `autonomous-worker-ops` — long unattended work

| | |
|--|--|
| **Question it answers** | “How do we keep **allowlisted** work running for **H hours** (or multi-day windows) without me babysitting chat?” |
| **Works for** | Any project with a job list: tests, refactors, inventory, codegen batches, doc rebuilds, eval suites |
| **Pattern** | **Worker** (time budget) + **Watchdog** (restart if dead) + **heartbeat/status** + **pause file** + **allowlist** + strip secrets |
| **Hours** | Human-set (e.g. 8 / 24 / 48). Multi-day is fine **if** the machine stays **awake**, and the watchdog can restart mid-window |
| **Call** | `/autonomous-worker-ops` or “design a 48h worker+watchdog for these jobs” |

**Why it exists:** Chat sessions die. Laptops sleep. Agents crash. A **worker + watchdog** is ops infrastructure, not “hope the terminal stays open.”

**Limits (accurate):**  
- Skill documents the pattern; **you** still need scripts + launchd/cron/systemd in *your* repo.  
- Jobs must be **allowlisted** — not open-ended “keep coding until perfect.”  
- **Not** auto-deploy, auto-trade, or unbounded internet actions.  
- **Host sleep** still kills the run if the laptop suspends — worker/watchdog cannot fix that alone.

**Stay awake (optional host tips):**

| OS | Prefer first | Optional |
|----|----------------|----------|
| **macOS** | Built-in `caffeinate -dims` (can wrap the worker process) | **[Amphetamine](https://apps.apple.com/app/amphetamine/id937984704)** (Mac App Store) — simple timed “don’t sleep” sessions; not required |
| **Windows** | Power settings: sleep **Never** while plugged in for the window; or `powercfg` standby timeout changes (restore after) | Third-party keep-awake tools (e.g. Caffeine / Don't Sleep) — optional, no single standard |
| **Most reliable** | Always-on mini-PC / VPS with suspend disabled | — |

---

## How they compose (recommended)

```text
                    ┌─────────────────────────────┐
  OS schedule ─────►│ Watchdog (every ~1 hour)    │
                    │ restart worker if dead/stale │
                    └──────────────┬──────────────┘
                                   ▼
                    ┌─────────────────────────────┐
                    │ Worker for H hours           │
                    │ allowlisted jobs only        │
                    │ heartbeat + pause file       │
                    └──────────────┬──────────────┘
                                   │ produces PRs, fixes, reports
                                   ▼
                    ┌─────────────────────────────┐
                    │ dual-agent-review            │
                    │ before merge / ship / spend  │
                    └──────────────┬──────────────┘
                                   ▼
                              Human if HUMAN_REQUIRED
```

| Concern | Skill |
|---------|--------|
| Keep work running overnight / multi-day | **autonomous-worker-ops** |
| Decide if results may be promoted | **dual-agent-review** |
| High-level “may we act at all?” ladder | **fail-closed-promotion** (optional) |

**Do not merge** dual-review and worker-ops into one skill: different cadence, different failure modes. **Do use both** on serious projects.

---

## Concrete examples

### Example A — App is broken; agents keep grinding safely

**Goal:** Flaky CI / failing e2e; you want progress for **24–48 hours** without sitting in chat.

1. **autonomous-worker-ops**  
   - Allowlist: `test`, `lint`, targeted fix scripts, “open PR with failing log + proposed patch”  
   - Hours: `48`  
   - Forbidden: production deploy, secret files, force-push main  
2. Worker loop: reproduce → minimal fix → re-run tests → write status  
3. When a candidate fix looks ready → **dual-agent-review** on the PR/diff  
4. **ACCEPT** → you merge; **REVISE** → one more loop; **HUMAN_REQUIRED** → you decide (e.g. prod data access)

**Accurate?** Yes — *if* jobs are bounded.  
**Not accurate:** “Agents never stop until the universe is fixed” with no time budget or allowlist. Prefer: *until the window ends or the suite is green, whichever first*, then review.

---

### Example B — Multi-day feature implementation

1. Human freezes scope (“v1 only: endpoints X, no payments”).  
2. Worker runs for several days of wall-clock time in **renewed H-hour windows** (or one long window if the host stays up): implement → test → document.  
3. End of each major chunk: dual-agent-review before merge.  
4. Ship to production only after human + ACCEPT (and your normal CI).

---

### Example C — Research / eval suite overnight

1. Allowlist: run eval jobs, write JSON reports, no network write except approved APIs.  
2. Watchdog restarts if the process dies.  
3. Morning: dual-agent-review on “are these results publishable / decision-grade?”

---

### Example D — Dual review alone (no worker)

You have a one-shot design or security-sensitive PR.  
Skip the worker. Run **dual-agent-review** only. Still valuable on any subject.

---

## Optional skills

### 3. `fail-closed-promotion` — “May we act?”

Short ladder: **FORBIDDEN → EXPLORE → CONFIRM → ACT (human-gated)**.  
Use for ship readiness, agent tool permission, or any claim that wants production side effects.  
Works **outside** investing (product flags, internal agents, etc.).

### 4. `investment-claim-court` — domain pack (not required for coding)

Grades **investment claims** (stocks, ETFs, crypto, macro) with:

`Reject | Watch | Research More | Small Position Allowed | Confirmed Thesis`

- **Not** a tip engine (“buy ETH”).  
- **Not** required to use dual-agent or worker-ops.  
- Include it only if you care about personal/process investing integrity.

If you only want engineering integrity, **install the first two (or three) skills** and ignore this one.

---

## Install

### Grok Build

```bash
git clone https://github.com/jfaccioli/agent-integrity-skills.git
cd agent-integrity-skills

# Core (recommended)
for s in dual-agent-review autonomous-worker-ops fail-closed-promotion; do
  mkdir -p ~/.grok/skills/$s && cp $s/SKILL.md ~/.grok/skills/$s/SKILL.md
done

# Optional investing
mkdir -p ~/.grok/skills/investment-claim-court
cp investment-claim-court/SKILL.md ~/.grok/skills/investment-claim-court/SKILL.md
```

Call: `/dual-agent-review`, `/autonomous-worker-ops`, `/fail-closed-promotion`, `/investment-claim-court`

### Claude Code

```bash
git clone https://github.com/jfaccioli/agent-integrity-skills.git
mkdir -p ~/.claude/skills/evidence
cp -R agent-integrity-skills/dual-agent-review \
      agent-integrity-skills/autonomous-worker-ops \
      agent-integrity-skills/fail-closed-promotion \
      ~/.claude/skills/evidence/
# optional:
cp -R agent-integrity-skills/investment-claim-court ~/.claude/skills/evidence/
```

### Codex / others

```text
Read and obey only:
.../dual-agent-review/SKILL.md
```

Or copy into that tool’s skills directory.

### Project-local

```bash
mkdir -p .grok/skills   # and/or .claude/skills
cp -R dual-agent-review autonomous-worker-ops fail-closed-promotion .grok/skills/
```

---

## What this is not

| Not | Reality |
|-----|---------|
| Infinite unconstrained agents | Time budget + allowlist |
| Auto production deploy | Human + dual review on promote |
| Live trading / broker bots | Explicitly out of scope |
| Same-model “LGTM” = independent audit | Labeled internal QA ≠ freeze authority |
| Stock tips | investment-claim-court refuses tips |

---

## License & disclaimer

MIT — see [LICENSE](LICENSE).

Process templates only. **Not financial advice.** No warranty. You own how agents run on your machines.

---

## Origin

Patterns extracted from real multi-hour research/ops loops and dual-review discipline (including a private lab that refused live trading when evidence did not clear hard gates). Published so the **integrity mechanics** travel across tools — not so anyone copy-pastes a trading strategy.
