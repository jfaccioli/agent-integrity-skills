---
name: autonomous-worker-ops
description: >
  Design or run a long-lived allowlisted worker plus watchdog for multi-hour
  agentic work without human babysitting. Use when the user runs
  /autonomous-worker-ops, asks for marathon, watchdog, scheduler, 24h/48h
  unattended jobs, launchd/cron worker, heartbeat, pause file, or keep agents
  working for N hours. Does not place trades, hold secrets, or replace dual-agent
  review. Compose with dual-agent-review for high-blast-radius promotion.
---

# Autonomous Worker Ops

Portable pattern for **time-boxed unattended work**.

**Job of this skill:** Help design, configure, or operate a **worker + watchdog** loop so allowlisted tasks keep running for **H hours** without the human sitting in chat.

**Not this skill:** Dual-model review, investment tips, live trading, secret management, or “keep going forever with no budget.”

## One-line split (do not merge with dual-agent-review)

| Concern | Skill |
|---------|--------|
| Keep safe batch work running for H hours | **autonomous-worker-ops** (this) |
| May we promote / merge / spend / act? | **dual-agent-review** + **fail-closed-promotion** |

They **compose**; they should **not** be one skill (different cadence, different failure modes).

```text
Watchdog ──restarts──► Worker (H hours, allowlisted jobs)
                              │
                              │ produces artefacts
                              ▼
                     dual-agent-review (on demand / on promote)
                              │
                              ▼
                     Human for secrets / money / irreversible
```

## Architecture

```text
Human sets H hours + allowlist + pause policy
        │
        ▼
┌──────────────────────────┐
│ WATCHDOG (periodic)      │  every ~1h (cron/launchd/systemd)
│ - pause file? → exit     │
│ - worker alive+fresh HB? │
│ - else start/restart     │
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ WORKER / MARATHON        │
│ - ends_at = now + H      │
│ - loop allowlisted jobs  │
│ - write heartbeat/status │
│ - strip secrets from env │
│ - stop on pause or ends  │
└──────────────────────────┘
```

## Required pieces (any language / repo)

| Piece | Purpose |
|-------|---------|
| **Worker entrypoint** | Single process that runs jobs until time budget ends |
| **Job allowlist** | Explicit scripts/commands only — no open-ended “do anything” |
| **Hours** | `WORKER_HOURS` or equivalent (human-defined, e.g. 8 / 24 / 48) |
| **Status JSON** | `status`, `pid`, `heartbeat_at`, `ends_at`, `last_job`, `jobs_done` |
| **Heartbeat freshness** | Watchdog treats stale HB (e.g. >10 min) as dead |
| **Pause file** | Human drop-file stops worker/watchdog path without killing OS |
| **Lock / single instance** | Avoid two workers writing the same state |
| **Logs** | Append-only log file for postmortems |
| **Opt-in flags** | Risky job classes off unless `FEATURE_X=1` |
| **External scheduler** | launchd / cron / systemd / CI schedule — **not** the chat session |

A **skill alone cannot** install launchd or keep a laptop awake. You still need OS scheduling + machine not fully asleep (or a VPS / always-on host).

## Keep the host awake (laptop reality)

Worker + watchdog only help if the **OS does not suspend** the machine for the whole window. Prefer a plugged-in always-on host when possible.

| Platform | Built-in (prefer first) | Optional apps |
|----------|-------------------------|---------------|
| **macOS** | `caffeinate -dims` (or wrap the worker: `caffeinate -dims ./worker …`) prevents idle sleep while running; System Settings → Energy / Battery → options when plugged in | **[Amphetamine](https://apps.apple.com/app/amphetamine/id937984704)** (free Mac App Store) — easy toggle sessions (“prevent sleep for 48h”, allow display off). Useful when you want GUI control without remembering flags |
| **Windows** | Settings → System → Power: set sleep to **Never** while plugged in for the run; or `powercfg /change standby-timeout-ac 0` (and restore after). Task Scheduler for watchdog | Third-party “keep awake” utilities exist (e.g. **Caffeine**, **Don't Sleep**, Microsoft PowerToys-related workflows) — quality varies; treat as optional. No single standard equal to Amphetamine |
| **Linux** | `systemd-inhibit`, `caffeinate`-like tools, or disable suspend on AC in power settings; `cron`/`systemd` timers for watchdog | Desktop “caffeine” applets (GNOME/KDE) optional |
| **Best reliability** | Small always-on mini-PC / VPS with no sleep | — |

**Guidance for agents using this skill:**

1. Mention host-sleep as a first-class failure mode (alongside process crash).  
2. Recommend **built-ins first** (`caffeinate` on Mac, power plan on Windows).  
3. Mention **Amphetamine on Mac** as a convenient optional app — **not required**, not a dependency of the skill.  
4. Do not assume Windows users have Amphetamine; point at power settings + optional keep-awake tools.  
5. Closing the lid on many laptops still suspends unless configured otherwise — call that out.

## Human knobs

```text
WORKER_HOURS=48          # how long the worker may run
WORKER_MAX_JOBS=0        # 0 = unlimited within hours
FEATURE_RISKY=0          # opt-in job classes
PAUSE_PATH=.../PAUSE     # touch to stop
STATUS_PATH=.../STATE.json
```

Document these in the project README when you adopt the pattern.

## Safety defaults (fail-closed)

1. **No secrets** in worker env (strip `*KEY*`, `*SECRET*`, `*PASSWORD*`, tokens).  
2. **No production deploy, order placement, or use of live secret values** from worker jobs.  
3. **Allowlist only** — never `eval` free-form user chat as the job list.  
4. **High-blast-radius changes** (shared business logic, production ship, destructive data ops) are **not** auto-ACCEPT; invoke **dual-agent-review** and human.  
5. Worker may **draft** and **run tests**; promotion is a separate step.  
6. Default job catalog should be **safe maintenance** if risky flags are off.

## When the user asks to “run for N hours”

1. Confirm **goal** and **allowlisted tasks** (bullet list).  
2. Confirm **H hours** and machine will stay available (**awake**: caffeinate / Amphetamine / power plan / VPS).  
3. Confirm **forbidden** actions (money, keys, force-push, etc.).  
4. Propose or wire: worker script, watchdog, status paths, pause path.  
5. Start / restart path; show how to verify:

```text
cat STATUS_PATH          # status=running, heartbeat fresh
tail LOG_PATH
# pause:
touch PAUSE_PATH
```

6. If they want dual review: schedule **manual** or **post-batch** `/dual-agent-review` on artefacts — not every tiny job unless cheap.

## Bundled reference implementation (this repository)

**Use these first** — self-contained, no private lab paths:

| Piece | Path |
|-------|------|
| Worker | `templates/worker/worker.py` |
| Watchdog | `templates/worker/watchdog.py` |
| Example jobs | `templates/worker/jobs.example.json` |
| How to copy/run | `templates/worker/README.md` |
| macOS launchd plist | `templates/macos/com.example.autonomous-worker.plist` |
| macOS install helper | `templates/macos/install_launchd.sh` |

Copy `worker.py` / `watchdog.py` into your app’s `scripts/`, set `WORKER_JOBS_FILE` to your allowlist, schedule the watchdog hourly.

**Env knobs (generic):** `WORKER_HOURS`, `WORKER_ROOT`, `WORKER_STATE`, `WORKER_PAUSE`, `WORKER_LOG_DIR`, `WORKER_JOBS_FILE`, `WORKER_SCRIPT`, `WORKER_AUTO_RESTART`, `WORKER_STALE_S`.

**Optional origin note:** The pattern was battle-tested in a private research lab; that lab’s paths are **not** required and are **not** shipped here.

## Checklist for a new project

```text
[ ] Worker script with ends_at = now + H hours
[ ] Status JSON + heartbeat each loop
[ ] Pause file honored
[ ] Single-instance lock
[ ] Allowlisted jobs only
[ ] Secrets stripped from child env
[ ] Watchdog interval (~1h) via OS scheduler
[ ] Stale heartbeat → restart worker
[ ] Host sleep prevented for the window (caffeinate / Amphetamine / power plan / VPS)
[ ] Logs directory
[ ] README: how to start / pause / set hours / stay awake
[ ] Promotion path documented → dual-agent-review (separate skill)
[ ] No live/money/keys in allowlist
```

## Output when designing (agent response shape)

```text
WORKER_PLAN:
  hours: H
  allowlist: [...]
  forbidden: [...]
  status_path: ...
  pause_path: ...
  watchdog: launchd|cron|systemd|manual
  opt_in_flags: [...]
COMPOSE_WITH_DUAL_REVIEW:
  when: (e.g. before merge / before any ACT)
  not_when: (each routine inventory job)
VERIFY:
  - ...
PAUSE:
  - touch ...
```

## Anti-patterns

- One mega-skill that both restarts processes **and** ACCEPT/REVISE science (confusing, over-invoked)  
- Worker that can enable LIVE or read `.env` secrets  
- Infinite restart after window ends without human `AUTO_RESTART`  
- “Autonomous” = unbounded tool use with no allowlist  
- Replacing dual review with “watchdog said healthy”  

## Compose (recommended)

| Situation | Use |
|-----------|-----|
| Keep tests / inventory / evals / backfills running 24–48h | **autonomous-worker-ops** |
| Before merge or production promotion of high-risk changes | **dual-agent-review** |
| Readiness ladders (any product: staging → prod, draft → published) | **fail-closed-promotion** |
| Investment claim grading only | **investment-claim-court** (optional domain skill; not the worker) |
