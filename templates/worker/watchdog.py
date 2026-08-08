#!/usr/bin/env python3
"""Generic watchdog: ensure worker is alive within its time window.

Run hourly via launchd / cron / Task Scheduler / systemd timer.
Restarts worker if dead or heartbeat stale while window still open.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("WORKER_ROOT", str(Path.cwd())))
STATE = Path(os.environ.get("WORKER_STATE", str(ROOT / "var" / "worker" / "STATE.json")))
PAUSE = Path(os.environ.get("WORKER_PAUSE", str(ROOT / "var" / "worker" / "PAUSE")))
LOG_DIR = Path(os.environ.get("WORKER_LOG_DIR", str(ROOT / "var" / "worker" / "logs")))
STATUS = Path(os.environ.get("WORKER_WATCHDOG_STATUS", str(ROOT / "var" / "worker" / "WATCHDOG_STATUS.json")))
WORKER_SCRIPT = Path(os.environ.get("WORKER_SCRIPT", str(Path(__file__).resolve().parent / "worker.py")))
STALE_S = int(os.environ.get("WORKER_STALE_S", str(10 * 60)))
AUTO_RESTART = os.environ.get("WORKER_AUTO_RESTART", "0") == "1"
PYTHON = os.environ.get("WORKER_PYTHON", sys.executable)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def log(msg: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"[{utcnow().isoformat()}] WATCHDOG {msg}"
    print(line, flush=True)
    with open(LOG_DIR / "watchdog.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state() -> dict:
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def strip_secrets(env: dict[str, str]) -> dict[str, str]:
    out = {}
    for k, v in env.items():
        ku = k.upper()
        if any(x in ku for x in ("API_KEY", "SECRET", "PASSWORD", "PRIVATE_KEY", "TOKEN", "CREDENTIAL")):
            continue
        out[k] = v
    return out


def start_worker() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "worker_daemon.log"
    env = strip_secrets(os.environ.copy())
    env.setdefault("WORKER_HOURS", env.get("WORKER_HOURS", "24"))
    env["WORKER_ROOT"] = str(ROOT)
    proc = subprocess.Popen(
        [PYTHON, str(WORKER_SCRIPT)],
        cwd=str(ROOT),
        env=env,
        stdout=open(log_path, "a", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    log(f"started worker pid={proc.pid}")
    return proc.pid


def main() -> int:
    if PAUSE.exists():
        log("paused")
        STATUS.parent.mkdir(parents=True, exist_ok=True)
        STATUS.write_text(
            json.dumps({"status": "paused", "at": utcnow().isoformat()}, indent=2) + "\n",
            encoding="utf-8",
        )
        return 0

    st = load_state()
    status = st.get("status")
    pid = st.get("pid")
    hb = st.get("heartbeat_at")
    ends = st.get("ends_at")

    alive = isinstance(pid, int) and pid_alive(pid)
    hb_age = None
    if hb:
        try:
            hb_age = (utcnow() - datetime.fromisoformat(hb)).total_seconds()
        except Exception:
            hb_age = None
    stale = hb_age is not None and hb_age > STALE_S
    window_open = True
    if ends:
        try:
            window_open = utcnow() < datetime.fromisoformat(ends)
        except Exception:
            window_open = True

    action = "none"
    if status == "running" and alive and not stale:
        action = "healthy"
        log(f"worker healthy pid={pid} hb_age={hb_age:.0f}s jobs={st.get('jobs_done')}")
    elif status == "running" and (not alive or stale) and window_open:
        action = "restart"
        log(f"worker dead/stale (alive={alive} stale={stale}) — restarting")
        start_worker()
    elif status in (None, "", "idle", "crashed") or (status == "completed" and AUTO_RESTART):
        action = "start"
        log(f"no active worker (status={status}) — starting")
        start_worker()
    elif status == "completed" and not window_open:
        action = "completed_window"
        log("worker window completed — not auto-restarting (set WORKER_AUTO_RESTART=1 to loop)")
    else:
        action = f"observe_{status}"
        log(f"observe status={status} alive={alive} window_open={window_open}")

    st2 = load_state()
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    STATUS.write_text(
        json.dumps(
            {
                "status": action,
                "at": utcnow().isoformat(),
                "worker": {
                    "status": st2.get("status"),
                    "pid": st2.get("pid"),
                    "jobs_done": st2.get("jobs_done"),
                    "ends_at": st2.get("ends_at"),
                    "last_job": st2.get("last_job"),
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
