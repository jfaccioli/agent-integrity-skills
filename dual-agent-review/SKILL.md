---
name: dual-agent-review
description: >
  Run a fail-closed producer/reviewer protocol for plans, diffs, claims, or
  designs. Use when the user runs /dual-agent-review, asks for dual-Grok,
  second-pair-of-eyes, hostile review, ACCEPT/REVISE/HUMAN_REQUIRED, handoff
  protocol, or independent QA before merge/freeze/spend. Portable across Grok,
  Claude, Codex, and other agents.
---

# Dual-Agent Review Protocol

Portable promotion/review protocol (inspired by dual-Grok / handoff systems).

**Goal:** Separate **producing** work from **permission to proceed**, so one model cannot silently approve its own high-blast-radius mistakes.

## Roles

| Role | Duty |
|------|------|
| **Producer** | Bounded proposal (plan, diff summary, claim, design) |
| **Reviewer** | Hostile, reproduce-minded; prefer kill over cheerlead |
| **Human** | Secrets, money movement, production enablement, unresolved disputes |

**Same model family may do Internal QA** but must **label** `reviewer_mode: internal_qa_not_independent`.  
**Independent review** = different product/vendor when available (e.g. Claude reviewing Grok, Codex reviewing Claude).

## Hard rules

1. Reviewer **does not** implement fixes in the same breath as ACCEPT (review-only).  
2. Decisions are exactly one of: **ACCEPT** | **REVISE** | **HUMAN_REQUIRED**.  
3. **At most one REVISE round.** Second material disagreement → HUMAN_REQUIRED.  
4. **HUMAN_REQUIRED cannot be self-cleared** by producer or same-model reviewer.  
5. Review text alone is not scientific/financial evidence; cite artefacts.  
6. Never authorize credentials, live trading, order placement, or irreversible data destruction without human.

## Always HUMAN_REQUIRED

- Creating, rotating, or **using real secret values** (API keys, tokens, production credentials)  
- Enabling production/live side effects (deploy to prod, real charges, customer-impacting automation)  
- Softening safety/evaluation gates to force a pass  
- Irreversible ops (force-push main, drop prod data) without explicit human  
- Spending paid third-party APIs / subscriptions without prior approval  
- Claiming “ready for production” on high blast-radius systems  

**Usually not HUMAN_REQUIRED alone:** documenting env var *names*, editing `.env.example`, adding placeholder config, or low blast-radius UI/copy.

## When to invoke (blast radius)

| Invoke dual-agent-review | Skip (routine) |
|--------------------------|----------------|
| Shared generation/scoring logic, prompts that affect all users | Narrow UI polish |
| Auth, billing, quotas, migrations | Typos, CSS, one-off copy |
| Production deploy config, redirects/canonicals, destructive ops | Trivial tests for local-only helpers |
| User explicitly asks for second opinion on a **high-risk** change | Every “LGTM?” on small diffs |

Prefer labeling `BLAST_RADIUS: low|medium|high`. For **low**, internal QA may suffice; for **high**, prefer independent model/vendor when available.

## When invoked

### Step 1 — Identify mode

- **A. Full dual** (two agents or two sessions): producer artefact exists → run reviewer  
- **B. Single-agent hostile QA**: one model plays reviewer against the user’s or its own prior proposal; mark `internal_qa_not_independent`

### Step 2 — Producer package (if missing, request or draft)

```text
HANDOFF_ID: YYYYMMDD-short-topic
FROM: producer
TO: reviewer
ARTEFACT: (path or paste summary)
AUTHORIZED_ACTIONS: (what proceed would allow)
FORBIDDEN_ACTIONS: (explicit)
TESTS_OR_PROBES: (how to verify)
BLAST_RADIUS: low | medium | high
```

### Step 3 — Reviewer checklist (must address)

1. What would make this **false** or **unsafe**?  
2. Missing holdout / pre-registration / evaluation freeze?  
3. Overclaim vs evidence?  
4. Secret or production creep?  
5. Can you **reproduce** a check (command, logic walk, counterexample)?  
6. Multiplicity / peeking / p-hacking?  

### Step 4 — Decision block (required)

```text
REVIEW_DECISION: ACCEPT | REVISE | HUMAN_REQUIRED
REVIEWER_MODE: independent | internal_qa_not_independent
BLAST_RADIUS: low | medium | high
FINDINGS:
- ...
REQUIRED_FIXES: (if REVISE; max one round)
HUMAN_ASK: (if HUMAN_REQUIRED; exact question)
PROCEED_MEANS: (what ACCEPT allows — bounded)
DOES_NOT_ALLOW: (list)
```

## ACCEPT criteria

- Bounded scope clear  
- No always-HUMAN items pending  
- Checks/probes addressed or explicitly deferred with label  
- For **high** blast radius: prefer independent reviewer; if only internal QA, ACCEPT only for “continue drafting,” **not** freeze/production/money  

## REVISE criteria

- Fixable gaps in one round  
- List exact required fixes; no vibe-only nitpicks  

## HUMAN_REQUIRED criteria

- Always-list items, or  
- Second disagreement after REVISE, or  
- Insufficient evidence for claimed permission level  

## Optional domain notes

- **Product apps (e.g. SEO/tools):** attach behavioural contract, affected surfaces, cache compatibility, staging check — project-specific fields belong in *your* fork/variant, not only in this generic skill.  
- **Investing:** if grading capital claims, use **investment-claim-court** separately; dual-agent-review stays for high-risk *engineering* or large-size permission, not daily tips.

## Anti-patterns

- “LGTM” without findings  
- Reviewer rewriting production code then ACCEPT  
- Infinite revise loops  
- Treating chat agreement as freeze authority  
