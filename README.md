# Agent Integrity Skills

Keep AI-agent work moving. Review its output separately. Keep production human-gated.

Three portable skills for **Claude Code**, **Codex**, **Grok Build**, **Cursor**, and similar coding agents.

| When this goes wrong | Add this skill | What changes |
| --- | --- | --- |
| Agent work stops when a session or process dies | [`autonomous-worker-ops`](autonomous-worker-ops/SKILL.md) | Bounded, allowlisted jobs can recover and continue |
| The agent approves its own work | [`dual-agent-review`](dual-agent-review/SKILL.md) | A separate review returns `ACCEPT`, `REVISE`, or `HUMAN_REQUIRED` |
| Green tests are mistaken for permission to ship | [`fail-closed-promotion`](fail-closed-promotion/SKILL.md) | Evidence must clear explicit gates before action |

Use all three for substantial product work, or adopt only the control your workflow is missing.

## Ask Your Agent First

Ask your AI coding agent to review these skills against your project's workflows, risks, and existing controls. It should recommend which skills are useful, what needs project-specific tailoring, and what should remain unchanged before installing anything.

```text
Review this repository against:
https://github.com/jfaccioli/agent-integrity-skills

Recommend:
- which skills are relevant
- where they would improve the current workflow
- what project-specific tailoring they need
- what existing controls must remain unchanged
- which actions must stay human-gated

Do not install or modify anything yet.
```

Project-local variants are encouraged. Rename states and add handoff fields to match your product, but do not weaken fail-closed defaults or existing safety controls.

## The Three Controls

### 1. Keep Work Moving

`autonomous-worker-ops` helps run allowlisted jobs inside a human-defined time window.

It combines a worker, heartbeat, status file, pause control, and watchdog recovery. It is useful for test runs, targeted refactors, inventory jobs, code generation, documentation rebuilds, and evaluation suites.

It does **not** authorize unlimited coding, production deployment, secret access, or unrestricted internet actions. The skill documents the pattern; your project still needs worker scripts, an OS scheduler, and a machine that remains available.

### 2. Review Work Separately

`dual-agent-review` prevents the producer from silently approving its own result.

The reviewer checks the actual plan, diff, claim, design, tests, and evidence, then returns exactly one decision:

- `ACCEPT`
- `REVISE`
- `HUMAN_REQUIRED`

The reviewer can be another model. A same-model hostile review is still useful internal QA, but it must be labeled `internal_qa_not_independent` and cannot independently authorize high-risk production, money, or irreversible actions.

### 3. Control Permission

`fail-closed-promotion` starts from **do not act**.

Evidence must move the work through:

```text
FORBIDDEN -> EXPLORE -> CONFIRM -> ACT (human-gated)
```

Use it for ship readiness, agent permissions, publication claims, or any decision where passing tests is necessary but not sufficient authority to act.

## How the Three Controls Work

```text
Human defines scope, time, allowlist, and forbidden actions
                              |
                              v
                 autonomous-worker-ops
                  keeps bounded work moving
                              |
                              v
                    artefacts and evidence
                              |
                              v
                    dual-agent-review
             ACCEPT | REVISE | HUMAN_REQUIRED
                              |
                              v
                  fail-closed-promotion
          FORBIDDEN -> EXPLORE -> CONFIRM -> ACT
                              |
                              v
                 human approval where required
```

The controls compose, but they remain separate:

- A healthy worker does not prove its output is correct.
- An accepted review does not automatically authorize production.
- A permission gate does not keep a crashed worker running.

## Example: A Failing Application

You want an agent to work on flaky CI or failing end-to-end tests for 24 hours without supervising every step.

1. Freeze the scope and allowlist tests, linting, targeted fixes, and status reporting.
2. Use `autonomous-worker-ops` to run until the suite is green or the time window ends.
3. Run `dual-agent-review` on the candidate diff and its test evidence.
4. Use `fail-closed-promotion` to decide whether the result remains exploratory, may move to staging, or needs a human decision.

Production deployment, secret access, destructive operations, and force-pushing the main branch remain forbidden unless a human explicitly authorizes them.

## Other Useful Patterns

### Multi-day feature implementation

Freeze the feature scope first. Run implementation and tests in bounded, renewable windows. Review major chunks before merge. Keep production behind normal CI and explicit human approval.

### Overnight research or evaluation

Allowlist evaluation jobs and report generation. Restrict network writes to approved APIs. Review whether the results are decision-grade or publishable the next morning.

### Review without a worker

For a one-shot architecture plan, security-sensitive change, or high-risk diff, use `dual-agent-review` by itself.

## Quick Start

Clone the repository:

```bash
git clone https://github.com/jfaccioli/agent-integrity-skills.git
cd agent-integrity-skills
```

### Grok Build

```bash
for s in dual-agent-review autonomous-worker-ops fail-closed-promotion; do
  mkdir -p ~/.grok/skills/$s
  cp $s/SKILL.md ~/.grok/skills/$s/SKILL.md
done
```

Call:

```text
/dual-agent-review
/autonomous-worker-ops
/fail-closed-promotion
```

### Claude Code

```bash
mkdir -p ~/.claude/skills/evidence
cp -R dual-agent-review \
      autonomous-worker-ops \
      fail-closed-promotion \
      ~/.claude/skills/evidence/
```

### Codex, Cursor, and Other Agents

Ask the agent to read and apply only the relevant skill files:

```text
Read and apply:
- .../autonomous-worker-ops/SKILL.md
- .../dual-agent-review/SKILL.md
- .../fail-closed-promotion/SKILL.md

First assess which skills fit this project and what must be tailored.
Do not install or modify anything until the assessment is complete.
```

For project-local installation, copy the selected skill directories into the skills location used by your agent and repository. Preserve each directory's `SKILL.md` filename.

## Tailor Them to Your Product

These are portable contracts, not a demand to impose identical terminology on every project.

| Skill | Typical tailoring |
| --- | --- |
| `autonomous-worker-ops` | Job allowlist, time budget, status paths, pause mechanism, scheduler, forbidden actions |
| `dual-agent-review` | Handoff fields, affected surfaces, required tests, blast-radius rules, review independence |
| `fail-closed-promotion` | Readiness-state names, evidence requirements, production and human gates |

Examples of valid state renaming include:

```text
FORBIDDEN -> EXPLORE -> CONFIRM -> ACT
BLOCKED   -> REVIEW  -> STAGING -> PRODUCTION (human-gated)
```

Changing names is fine. Removing evidence requirements or allowing an agent to self-clear a human gate is not.

## Bundled Worker Templates

The repository includes a self-contained reference implementation:

- [`templates/worker/worker.py`](templates/worker/worker.py) - bounded worker loop
- [`templates/worker/watchdog.py`](templates/worker/watchdog.py) - stale-process recovery
- [`templates/worker/jobs.example.json`](templates/worker/jobs.example.json) - example allowlist
- [`templates/worker/README.md`](templates/worker/README.md) - setup and operation
- [`templates/macos/com.example.autonomous-worker.plist`](templates/macos/com.example.autonomous-worker.plist) - example macOS LaunchAgent
- [`templates/macos/install_launchd.sh`](templates/macos/install_launchd.sh) - example installer

Copy the templates into your project, define the allowlisted jobs, and schedule the watchdog with launchd, cron, systemd, or an equivalent external scheduler.

## Host Availability

A worker and watchdog cannot recover while the host is fully asleep.

| Platform | Prefer first | Optional |
| --- | --- | --- |
| macOS | Built-in `caffeinate -dims` or suitable power settings | [Amphetamine](https://apps.apple.com/app/amphetamine/id937984704) for timed keep-awake sessions |
| Windows | Power settings or `powercfg`; restore temporary changes afterward | Third-party keep-awake tools where appropriate |
| Linux | `systemd-inhibit`, power settings, cron, or systemd timers | Desktop caffeine utilities |
| Most reliable | Always-on mini-PC or VPS with suspend disabled | - |

Closing a laptop lid may still suspend it. Confirm host behavior before relying on a multi-hour window.

## Boundaries

| This toolkit is not | What it actually provides |
| --- | --- |
| An infinite autonomous agent | A human-set time budget and explicit job allowlist |
| Automatic production deployment | Review and promotion controls with human gates |
| Proof that an agent's output is correct | A reproducible, evidence-seeking review protocol |
| Independent review when one model reviews itself | Internal QA labeled as non-independent |
| Secret management | Explicit restrictions on live credentials and sensitive actions |
| A production service or SLA | Instruction packs and minimal worker templates to adapt |

`HUMAN_REQUIRED` cannot be cleared by the producer or a same-model reviewer. Production, live secrets, payments, and irreversible actions remain human decisions.

## Optional Domain Pack

[`investment-claim-court`](investment-claim-court/SKILL.md) is a separate skill for grading investment claims:

```text
Reject | Watch | Research More | Small Position Allowed | Confirmed Thesis
```

It is not a tip engine, trading bot, or requirement for engineering projects. Skip it unless you specifically need an investment-claim process.

## Quality Status

Good to share as an opinionated integrity toolkit with worker templates.

Honest limits:

- Skills are instruction packs; results depend on the agent following them.
- Worker templates are minimal and require a real project-specific allowlist.
- The launchd helper is a macOS example; Linux and Windows scheduling are documented, not fully scripted.
- Agent harnesses differ, so installation paths and invocation behavior may require adjustment.
- Project-specific readiness states, ownership rules, tests, and handoff fields belong in your local adaptation.

If installation fails, open an issue with your operating system, agent, installation path, and the command or error involved.

## License and Disclaimer

MIT - see [LICENSE](LICENSE).

Process templates only. Not financial advice. No warranty. You remain responsible for how agents run and what actions they are permitted to take.

## Origin

These patterns were extracted from multi-hour research and operations workflows and dual-review discipline. They are published so the integrity mechanics can travel across tools and projects, not so high-risk decisions become automatic.
