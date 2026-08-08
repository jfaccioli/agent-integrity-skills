#!/usr/bin/env python3
"""Generic time-boxed allowlisted worker (portable template).

Copy into your repo, edit discover_jobs(), set WORKER_* env vars.
Does not deploy, trade, or load secrets by design.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Prefer WORKER_ROOT; else parent of scripts/ if this file lives at scripts/worker.py; else cwd.
_here = Path(__file__).resolve()
if os.environ.get("WORKER_ROOT"):
    ROOT = Path(os.environ["WORKER_ROOT"]).resolve()
elif _here.parent.name == "scripts":
    ROOT = _here.parents[1]
elif _here.parent.name == "worker":
    # Running from templates/worker/ during smoke tests
    ROOT = Path.cwd()
else:
    ROOT = Path.cwd()

STATE = Path(os.environ.get("WORKER_STATE", str(ROOT / "var" / "worker" / "STATE.json")))
PAUSE = Path(os.environ.get("WORKER_PAUSE", str(ROOT / "var" / "worker" / "PAUSE")))
LOG_DIR = Path(os.environ.get("WORKER_LOG_DIR", str(ROOT / "var" / "worker" / "logs")))
LOCK = LOG_DIR / "worker.lock"
DEFAULT_HOURS = float(os.environ.get("WORKER_HOURS", "24"))
TICKET_GAP_S = int(os.environ.get("WORKER_JOB_GAP_S", "30"))
CYCLE_GAP_S = int(os.environ.get("WORKER_CYCLE_GAP_S", "300"))


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def log(msg: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{utcnow().isoformat()}] WORKER {msg}"
    print(line, flush=True)
    with open(LOG_DIR / "worker.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_state(**kwargs) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    cur: dict = {}
    if STATE.exists():
        try:
            cur = json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:
            cur = {}
    cur.update(kwargs)
    cur["heartbeat_at"] = utcnow().isoformat()
    cur["pid"] = os.getpid()
    STATE.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8")


def strip_secrets(env: dict[str, str]) -> dict[str, str]:
    out = {}
    for k, v in env.items():
        ku = k.upper()
        if any(x in ku for x in ("API_KEY", "SECRET", "PASSWORD", "PRIVATE_KEY", "TOKEN", "CREDENTIAL")):
            continue
        out[k] = v
    return out


def discover_jobs() -> list[list[str]]:
    """Return allowlisted commands as argv lists.

    Edit this for your project. Prefer explicit list over globs of untrusted paths.
    Example: [["python", "-m", "pytest", "-q"], ["python", "scripts/inventory.py"]]
    """
    # Optional JSON allowlist: [{"argv": ["python", "-m", "pytest", "-q"]}, ...]
    jobs_path = Path(os.environ.get("WORKER_JOBS_FILE", str(ROOT / "var" / "worker" / "jobs.json")))
    if jobs_path.exists():
        data = json.loads(jobs_path.read_text(encoding="utf-8"))
        jobs = []
        for item in data:
            argv = item.get("argv") if isinstance(item, dict) else item
            if isinstance(argv, list) and argv:
                jobs.append([str(x) for x in argv])
        if jobs:
            return jobs
    # Safe default: no-op heartbeat job (replace in real projects)
    return [[sys.executable, "-c", "print('worker idle — configure WORKER_JOBS_FILE or discover_jobs()')"]]


def main() -> int:
    hours = float(os.environ.get("WORKER_HOURS", DEFAULT_HOURS))
    max_jobs = int(os.environ.get("WORKER_MAX_JOBS", "0"))
    ends = utcnow() + timedelta(hours=hours)

    if PAUSE.exists():
        log("PAUSE present at start — exit")
        write_state(status="paused", message="pause at start")
        return 0

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK.exists():
        try:
            old = int(LOCK.read_text(encoding="utf-8").strip().split()[0])
            os.kill(old, 0)
            log(f"another worker pid={old} alive — exit")
            return 0
        except Exception:
            LOCK.unlink(missing_ok=True)
    LOCK.write_text(f"{os.getpid()} {utcnow().isoformat()}\n", encoding="utf-8")

    jobs = discover_jobs()
    write_state(
        status="running",
        started_at=utcnow().isoformat(),
        ends_at=ends.isoformat(),
        hours=hours,
        jobs_done=0,
        last_job=None,
        job_catalog=[" ".join(j) for j in jobs],
        finished_at=None,
        error=None,
    )
    log(f"START hours={hours} ends={ends.isoformat()} n_jobs={len(jobs)}")

    env = strip_secrets(os.environ.copy())
    jobs_done = 0
    job_i = 0
    try:
        while utcnow() < ends:
            if max_jobs > 0 and jobs_done >= max_jobs:
                log(f"hit max_jobs={max_jobs}")
                break
            if PAUSE.exists():
                log("PAUSE detected — stopping")
                write_state(status="paused", jobs_done=jobs_done, message="human pause")
                return 0

            jobs = discover_jobs()
            if not jobs:
                log("no jobs — sleep cycle")
                time.sleep(CYCLE_GAP_S)
                write_state(status="running", jobs_done=jobs_done)
                continue

            argv = jobs[job_i % len(jobs)]
            job_i += 1
            label = " ".join(argv)
            log(f"JOB start {label}")
            write_state(status="running", last_job=label, last_job_started=utcnow().isoformat(), jobs_done=jobs_done)
            try:
                proc = subprocess.run(
                    argv,
                    cwd=str(ROOT),
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=int(os.environ.get("WORKER_JOB_TIMEOUT_S", str(40 * 60))),
                )
                log(f"JOB end code={proc.returncode}")
                if proc.returncode != 0 and proc.stderr:
                    log("stderr: " + proc.stderr.replace("\n", " | ")[:500])
            except Exception as e:
                log(f"JOB error {type(e).__name__}: {e}")
            jobs_done += 1
            write_state(jobs_done=jobs_done, last_job_finished=utcnow().isoformat())
            time.sleep(TICKET_GAP_S)
            if job_i % max(len(jobs), 1) == 0:
                time.sleep(CYCLE_GAP_S)

        write_state(
            status="completed",
            jobs_done=jobs_done,
            finished_at=utcnow().isoformat(),
            message="time window ended",
        )
        log(f"DONE jobs_done={jobs_done}")
        return 0
    finally:
        LOCK.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
