# Generic worker + watchdog templates

Self-contained **reference implementation** for `autonomous-worker-ops`.  
No crypto lab, no private paths — copy into any project.

## Layout after copy

Recommended:

```text
your-repo/
  scripts/
    worker.py      # from worker.py
    watchdog.py    # from watchdog.py
  var/worker/
    jobs.json      # from jobs.example.json
    STATE.json     # created at runtime
    PAUSE          # touch to stop
    logs/
```

Or keep paths via env (`WORKER_STATE`, `WORKER_JOBS_FILE`, …).

## Quick test (foreground)

```bash
cd your-repo
export WORKER_ROOT="$(pwd)"
export WORKER_HOURS=1
export WORKER_JOBS_FILE=var/worker/jobs.json
export WORKER_STATE=var/worker/STATE.json
export WORKER_PAUSE=var/worker/PAUSE
export WORKER_LOG_DIR=var/worker/logs
export WORKER_SCRIPT=scripts/worker.py

mkdir -p var/worker
cp /path/to/agent-integrity-skills/templates/worker/jobs.example.json var/worker/jobs.json
# after copying scripts:
python scripts/worker.py
```

## Watchdog (hourly)

```bash
export WORKER_ROOT="$(pwd)"
export WORKER_SCRIPT=scripts/worker.py
python scripts/watchdog.py
```

Schedule with:

| OS | Tool |
|----|------|
| macOS | launchd (see `templates/macos/`) |
| Linux | cron or systemd timer |
| Windows | Task Scheduler |

## Stay awake (laptops)

| OS | Prefer | Optional |
|----|--------|----------|
| macOS | `caffeinate -dims` | Amphetamine (App Store) |
| Windows | Power plan sleep Never on AC | Caffeine / Don't Sleep |
| Always-on | VPS / mini-PC | — |

## Safety

- Edit `discover_jobs()` / `jobs.json` to an **allowlist** only  
- Secrets stripped from child env by keyword  
- No deploy/trade built in  
- Use **dual-agent-review** before promoting worker output to production  

## Pause

```bash
touch var/worker/PAUSE
```
