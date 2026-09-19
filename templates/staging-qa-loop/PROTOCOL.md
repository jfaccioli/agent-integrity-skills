# Staging QA loop (QA ↔ Build)

Human is not in the inner loop. **Staging only. No production.**

Copy this file into the project (default `.handoffs/qa-loop/PROTOCOL.md`) and
tailor the knobs in **Project knobs**. Do not weaken the hard limits.

## Project knobs (tailor these)

| Knob | Fill in |
|------|---------|
| Staging URL | |
| Working branch | |
| Tester account | Authorized staging tester; never production users |
| Handoff dir | `.handoffs/qa-loop/` unless you choose another |
| Area sequence | Auth → core journeys → regression (replace with yours) |
| Product acceptance skills | Project-local skills the loop must load |
| Forbidden actions | Production, live payments, secret values, default-branch merge, … |
| Out of scope | Surfaces the human owns and QA must leave |

Product-specific scoring, ownership, billing, and content rules belong **here
or in project skills**, not in the portable `staging-qa-loop` skill.

## Roles

| Role | Does | Does not |
|------|------|----------|
| **QA** | Independent senior QA on staging with the authorised tester | Product code, production, billing, guessing passwords |
| **Build** | Engineering lead: triage, implement, test, commit, staging deploy | Production, default-branch merge, QA browser |
| **Human** | Production, secrets, billing/auth/datastore architecture, genuine product trade-offs | Per-bug chat |

QA publishes evidence. Build changes product code. Communication is **git on
the working branch**, not chat with the human.

If QA cannot push git, it writes the same `report.json` locally and records
`git_push_blocked`. The loop is not unattended until git works.

**Wake rule:** a QA git push does **not** start Build by itself. Unattended
Build needs an external watcher (`autonomous-worker-ops` or equivalent) that
fetches the branch and wakes Build only when `cycles/NNN/report.json` exists
on origin without `cycles/NNN/build.md`. If the Build session ends, the
watcher ends and the human is back in the middle.

## Git identities

- **QA** commits and pushes **only** cycle artefacts under the handoff
  `cycles/` directory (`report.json`, screenshots). It does not edit product
  code, workflows, or this protocol unless the human explicitly expands that
  allowlist.
- **Build** commits product code and `cycles/NNN/build.md` plus `STATE.json`.
- Pull requests to the default branch use the **human's** GitHub login, not
  the QA token.

## Cycle numbering

- `000` = pre-loop checkpoint (this protocol + known-good staging SHA).
- `001+` = QA pass then Build batch.
- Directory: `cycles/NNN/`
- `STATE.json` is the only live pointer.

```text
cycle N
  QA    -> deep QA of the current area (+ regression of prior areas)
        -> writes cycles/NNN/report.json (+ screenshots)
        -> commits/pushes that report on this branch
  Build -> git pull
        -> verify / triage / group / root-cause
        -> implement one coherent batch
        -> local tests
        -> checkpoint commit + staging deploy
        -> writes cycles/NNN/build.md
        -> asks QA for cycle N+1
repeat until stop criteria
```

## QA report (required)

Write `cycles/NNN/report.json` using `SCHEMA.md`. Screenshots go in
`cycles/NNN/screenshots/` and are referenced by relative path.

One pass = one area thoroughly, plus regression of previously closed P0/P1
IDs. Do not file one finding and stop.

Capture every screenshot in **this** cycle. Do not copy files from prior
cycles. Byte-identical images are invalid. If a claimed string is the
finding, the new shot must include that string in-frame.

If the executor cannot drive the staging browser, record
`{ "reason": "browser_tools_unavailable", "surface": "<area>" }` in
`blocked`, leave `findings` empty, and do **not** mark journeys passed.

## Priorities

- **P0** blocker, data-loss, security, cannot continue a core journey
- **P1** major broken workflow or materially wrong result
- **P2** real bug or UX that costs a normal user time, or that makes the
  product feel inaccurate, inefficient, or untrustworthy
- **P3** polish / optional — fix with a batch when cheap, else document

Do not inflate. Split **defect** vs **enhancement**.

Duplicates: reuse the previous issue ID and set `duplicate_of`. Do not open a
new ID for the same root cause.

## Build batch rules

1. Read the full report. Independently verify P0/P1 in code (and locally
   where possible).
2. Reject false positives. Merge duplicates to root cause.
3. Implement compatible fixes together. Prefer one root-cause change over
   five patches.
4. Do not rewrite auth, billing, or datastore architecture in this loop.
5. No production. No default-branch merge.
6. Local validation of touched tests is mandatory. Broader suites when the
   batch is shared/high-blast.
7. **Commit** only when the batch is coherent and tests for it pass.
8. **Staging deploy** only after that commit. One deploy per cycle unless a
   P0 hotfix is required.
9. Cap **3** unsuccessful repair attempts per issue, then record it
   `blocked` with cause.
10. High-blast batches invoke **dual-agent-review**. Same-model review is
    `internal_qa_not_independent` and cannot authorize production.

## Area sequence (replace with yours)

Stay on the current area until that journey is accurate, then move. Skip
ahead only if a P0 in a later **in-scope** area is already proven.

1. Auth / session / onboarding
2. Primary workspace after login
3. Core create / save / reopen journeys
4. The product's distinctive work queue or output
5. Cross-app errors, refresh, mobile
6. Broad regression of the above

## Stop and notify the human

Stop changing code when:

- no known P0 or unresolved P1
- frozen in-scope journeys work without guidance
- remaining P2s do not undermine accuracy or trust
- repeated QA passes are not finding significant new P1s
- relevant automated tests pass
- staging is stable for those journeys
- out-of-scope surfaces are listed as **human-owned**, never as “untested
  product that QA signed off”

Then wait for the human's staging review. Never production without them.

## Escalate (stop the loop)

- Production / default branch / flags / billing / live payments
- Destructive data or migrations
- Auth, identity-provider, or datastore replacement
- Security incident
- Genuine product trade-off where guessing is dangerous
- QA cannot authenticate or cannot publish reports to git
- Same P0 survives 3 Build batches
