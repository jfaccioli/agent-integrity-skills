---
name: fail-closed-promotion
description: >
  Apply a fail-closed promotion ladder to any claim or feature: Forbidden,
  Explore, Confirm, Act (human-gated). Use when the user runs
  /fail-closed-promotion, asks “may we act”, promotion ladder, explore vs
  confirm, ship readiness, agent permission, or PATH_C-style stop. Default is
  no production action.
---

# Fail-Closed Promotion Ladder

**Core question:** **May we act on this claim?**

Default answer: **No** until evidence clears a frozen bar.

## Permission states

| State | Meaning | Typical next step |
|-------|---------|-------------------|
| **FORBIDDEN** | Do not act; do not market as proven | Kill or archive claim |
| **EXPLORE** | Temporary / sandbox / draft only | Pre-reg tests; no production side effects |
| **CONFIRM** | Second window / untouched protocol only | Confirmatory eval |
| **ACT (human-gated)** | Production-adjacent only after ladder + human | Human explicit enable |

## Mapping (investment language)

| Promotion state | Investment claim court |
|-----------------|------------------------|
| FORBIDDEN | Reject |
| EXPLORE | Watch / Research More / exploratory tests |
| CONFIRM | Confirmatory path only |
| ACT (human) | Small Position Allowed or Confirmed Thesis **with human size rules** — never autotrade |

## Procedure

1. **Name the claim** in one sentence.  
2. **Name the action** that “act” would mean (trade, ship feature, enable agent tool, spend money).  
3. **Freeze evaluation rules** before looking at more results (or admit peeking → stay EXPLORE).  
4. Assign **one** permission state + evidence missing for the next state.  
5. If action is money/keys/customers/irreversible → ACT requires **human**; recommend dual-agent-review.

## Output block

```text
CLAIM:
ACTION_IF_PROMOTED:
PERMISSION_STATE: FORBIDDEN | EXPLORE | CONFIRM | ACT_HUMAN_GATED
WHY:
- ...
MISSING_FOR_NEXT_STATE:
- ...
HARD_STOPS_HIT: none | (list)
DISCLAIMER: Fail-closed. No production/money action without human when required.
```

## Hard stops (never skip)

- Softening gates to invent survivors  
- Self-clearing HUMAN_REQUIRED  
- Equating “interesting demo” with ACT  
- Live trading / order placement without human ladder  

## Empty promotion is success

If nothing reaches ACT: say so clearly. That is valid integrity output.
