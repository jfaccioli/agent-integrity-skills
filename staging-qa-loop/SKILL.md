---
name: staging-qa-loop
description: >
  Keep staging honest with an independent QA ↔ engineering cycle: git-handoff
  reports, unique evidence, staging-only batches, no production. Use when the
  user runs /staging-qa-loop, asks to keep staging honest, set up a Bot/Build
  QA loop, independent staging QA, cycle reports, STATE.json handoff, or a
  staging evidence loop. Compose with autonomous-worker-ops,
  dual-agent-review, and fail-closed-promotion. Does not authorize production.
---

# Staging QA Loop

**Core question:** **Is staging still lying?**

**Job of this skill:** Install or run a **two-role** loop so independent QA
evidence, not the implementer, decides whether staging journeys are honest.

**Not this skill:** Production deploy, dual-review of a diff, worker/watchdog
recovery, or product-specific acceptance rules. Put those in your project
protocol and in the other integrity skills.

## One-line split (do not merge)

| Concern | Skill |
|---------|--------|
| Keep a host/process running for H hours | **autonomous-worker-ops** |
| Keep staging journeys honest with independent evidence | **staging-qa-loop** (this) |
| May we accept this plan/diff/claim? | **dual-agent-review** |
| May we act / ship production? | **fail-closed-promotion** |

They **compose**. They are **not** one skill.

```text
Human freezes staging URL, tester, areas, forbidden actions
                    |
                    v
         autonomous-worker-ops (optional)
          keeps the cycle runner/watch alive
                    |
                    v
              staging-qa-loop
   QA pass (evidence) --> Build batch (staging only)
                    |
                    v
            dual-agent-review
     ACCEPT | REVISE | HUMAN_REQUIRED
                    |
                    v
          fail-closed-promotion
  FORBIDDEN -> EXPLORE -> CONFIRM -> ACT (human-gated)
                    |
                    v
         human approval for production
```

A green test suite does not prove staging is honest. A green staging loop does
not authorize production.

## Roles

| Role | Does | Does not |
|------|------|----------|
| **QA** | Independent senior QA on **staging**. Writes cycle evidence. | Product code, production, billing, guessing secrets |
| **Build** | Engineering lead: triage, implement, test, staging deploy | Production, main merge, driving the QA browser |
| **Human** | Production, secrets, billing/auth/datastore architecture, genuine product trade-offs | Per-bug chat inside a healthy loop |

QA and Build should be **separate sessions or products** when available. A
same-model split is still useful, but label it `internal_qa_not_independent`
and do not let it authorize production.

**Runtimes (examples, not requirements):** Grok Bot is a valid QA runtime
when it can drive a staging browser. Grok Build, Claude Code, Codex, or
Cursor can be the Build runtime. The contract is the roles and git handoff,
not the vendor.

## Required pieces

Copy [`templates/staging-qa-loop/`](../templates/staging-qa-loop/) into the
project (default `.handoffs/qa-loop/`):

| Piece | Purpose |
|-------|---------|
| `STATE.json` | Only live pointer: cycle, phase, branch, next area, stop |
| `PROTOCOL.md` | Project operating contract (tailor areas and forbidden actions) |
| `SCHEMA.md` | Cycle `report.json` shape |
| `cycles/NNN/` | One directory per cycle: `report.json`, screenshots, `build.md` |

Also required, outside the templates:

- A **staging** URL and an authorized tester account
- A working **git branch** both roles can use
- **Separate git identities**: QA writes cycle artefacts only; engineering
  PRs use the human's GitHub login, not the QA token
- A **wake path** if the loop should run unattended (see
  `autonomous-worker-ops`). A QA git push does **not** start Build by itself.

## Cycle

```text
cycle N
  QA    -> deep-test current area (+ regression of prior closed P0/P1)
        -> writes cycles/NNN/report.json (+ unique screenshots)
        -> commits/pushes only cycle artefacts
  Build -> git pull
        -> verify / triage / reject false positives
        -> implement one coherent staging batch (see Deploy batching)
        -> local tests for that batch
        -> ONE staging deploy for that batch
        -> writes cycles/NNN/build.md (Ship now / Park / Bot retest list)
        -> STATE -> awaiting QA for N+1
repeat until stop criteria or STATE.stop
```

Communication is **git on the working branch**, not chat with the human.

## Deploy batching

Staging deploys are expensive for the QA role. Batch so **one ship gets one
deep pass**.

1. **Batch related fixes into ONE staging deploy.** Compatible root-cause
   fixes that QA can retest together ship together. Do not drip one-line
   deploys through the loop.
2. **One Bot deep-pass per ship**, plus light regression of previously closed
   P0/P1 IDs. Do not request a full-area deep pass on every tiny patch.
3. **Do not rotate areas on an unchanged hosting SHA.** `STATE.next_area`
   moves only after this ship is on staging and QA has evidence against that
   SHA. If hosting still serves the previous build, stay on the same area;
   wait or redeploy. Do not ask QA to deep-test a new area on old bits.
4. **Single-shot deploys only for true P0 / trust blockers** — cannot continue
   a core journey, data-loss, security, or a lie that would ship as success.
   Everything else waits for the next batch.
5. **`build.md` must list:**
   - **Ship now** — what is in this deploy, git SHA, tests run
   - **Park** — accepted findings deferred, with why
   - **Bot retest list** — exact journeys/IDs QA must cover next (deep on the
     ship, light regressions)

A parked item is not a silent drop. It stays in `STATE` / later `build.md`
until shipped or explicitly `wontfix`.

## Hard rules

1. **Staging only.** No production deploy, no merge to the default branch, no
   live payments, no customer-data destruction.
2. **QA does not implement.** Build does not mark journeys passed without
   QA evidence from **this** cycle.
3. **Evidence is unique.** Screenshots and logs belong to this cycle. Do not
   copy prior-cycle artefacts. Byte-identical reuse is invalid.
4. **STATE.json is the only live pointer.** Do not invent the next area in
   chat.
5. **False positives are rejected.** Build independently verifies P0/P1 in
   code. Duplicates reuse the previous issue ID.
6. **One coherent batch and one staging deploy per cycle** (see Deploy
   batching). Prefer one root-cause change over five patches. Cap **3**
   unsuccessful repairs per issue, then `blocked`.
7. **Tests that cover the batch are mandatory.** Do not claim done on skipped
   tests.
8. **High-blast Build batches** invoke **dual-agent-review**. QA evidence is
   not a substitute for reviewing the diff.
9. **Green staging is CONFIRM at most.** Production remains
   **fail-closed-promotion** + human. QA/Build cannot self-clear
   `HUMAN_REQUIRED`.
10. **Do not put product-specific acceptance rules in this skill.** Tailor
    `PROTOCOL.md` in the project.

## When invoked

1. If the project has no loop, copy the templates, freeze staging URL /
   tester / area sequence / forbidden actions, and stop for human confirmation
   of those knobs.
2. If the loop exists, operate **one** cycle from `STATE.json`.
3. If there is no new QA report, do not invent work. Status is `blocked:
   awaiting cycle NNN report` (or the reverse if Build has not written
   `build.md`).
4. If unattended operation is requested, compose with
   **autonomous-worker-ops** for the watcher/wake path. Do not pretend a chat
   session is a scheduler.

## Output block

```text
STAGING_QA:
  cycle: NNN
  phase: awaiting_qa | awaiting_build | stopped | blocked
  area: ...
  environment: staging
  git_sha_tested: ...
  findings: P0= P1= P2= P3=
  rejected_false_positives: ...
  shipped_this_cycle: ...
  hosting_sha: ...
  ship_now: ...
  park: ...
  bot_retest_list: ...
  next_area: ...
  stop: true|false
COMPOSE:
  worker: (wake/watch path, or none)
  dual_review: (invoked | not needed | HUMAN_REQUIRED)
  promotion: FORBIDDEN | EXPLORE | CONFIRM | ACT_HUMAN_GATED
DOES_NOT_ALLOW:
  - production
  - ...
```

## Stop and escalate

Stop changing product code when staging journeys in the frozen area sequence
are accurate, stable, and not finding new P1s — then wait for **human**
staging review. Never production without the human.

Escalate (set `STATE.stop`, notify the human) on:

- Production / default-branch / feature-flag / billing / live payment pressure
- Destructive data or schema migrations
- Auth, identity-provider, or datastore replacement
- Security incident
- Genuine product trade-off where guessing is dangerous
- QA cannot authenticate or cannot publish reports to git
- The same P0 survives 3 Build batches

## Anti-patterns

- Implementer approving their own staging pass
- Reusing screenshots or claiming a journey passed without a browser
- Equating unit tests, a healthy worker, or “no P0 filed” with production
- QA token opening engineering PRs (or the human token used as the QA bot)
- Product-specific scoring/ownership/billing rules copied into this skill
- Infinite polish cycles after stop criteria are met
- Rotating `next_area` while staging still serves the previous SHA
- One finding → one deploy → one full-area retest, unless it is a P0 / trust blocker

## Templates

| File | Path |
|------|------|
| Protocol | `templates/staging-qa-loop/PROTOCOL.md` |
| Report schema | `templates/staging-qa-loop/SCHEMA.md` |
| State pointer | `templates/staging-qa-loop/STATE.json` |
| Cycles dir | `templates/staging-qa-loop/cycles/` |

Copy into the project, then tailor **only** the protocol: area sequence,
tester, forbidden actions, and project-specific acceptance skills. Do not
weaken fail-closed defaults.
