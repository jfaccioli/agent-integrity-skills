# Agent Integrity Skills

Portable **SKILL.md** packs for Grok Build, Claude Code, Codex, Cursor, and similar agents.

**Theme:** keep agents productive **without** letting them approve their own high-stakes mistakes — and without turning “AI” into fake investment tips.

Battle-tested ideas from a private evidence/research lab that **kept live trading off** when nothing cleared frozen gates.

## Skills (compose; don’t merge)

| Skill | Use when | Slash (Grok) |
|-------|----------|--------------|
| **dual-agent-review** | Plan/diff/claim needs hostile review | `/dual-agent-review` |
| **autonomous-worker-ops** | Multi-hour allowlisted worker + watchdog | `/autonomous-worker-ops` |
| **fail-closed-promotion** | “May we act?” Explore → Confirm → Act (human) | `/fail-closed-promotion` |
| **investment-claim-court** | Grade investment *claims* (not tips) | `/investment-claim-court` |

```text
Worker (H hours, allowlist)  →  artefacts
                                    ↓
                         dual-agent-review (on promote)
                                    ↓
                         human for secrets / money / irreversible
```

## Install

### Grok Build

```bash
git clone https://github.com/jfaccioli/agent-integrity-skills.git
cd agent-integrity-skills
for s in dual-agent-review autonomous-worker-ops fail-closed-promotion investment-claim-court; do
  mkdir -p ~/.grok/skills/$s
  cp $s/SKILL.md ~/.grok/skills/$s/SKILL.md
done
```

Then: `/dual-agent-review`, `/autonomous-worker-ops`, etc. Or `/skills`.

### Claude Code

```bash
git clone https://github.com/jfaccioli/agent-integrity-skills.git
mkdir -p ~/.claude/skills/evidence
cp -R agent-integrity-skills/dual-agent-review \
      agent-integrity-skills/autonomous-worker-ops \
      agent-integrity-skills/fail-closed-promotion \
      agent-integrity-skills/investment-claim-court \
      ~/.claude/skills/evidence/
```

Say: *Use the dual-agent-review skill* or *Read and follow …/SKILL.md*.

### Codex / other agents

Point the agent at a skill file:

```text
Read and obey only:
/path/to/agent-integrity-skills/dual-agent-review/SKILL.md
```

Or copy into that tool’s skills directory (e.g. `~/.agents/skills/` where supported).

### Project-local (optional)

```bash
cp -R dual-agent-review autonomous-worker-ops fail-closed-promotion investment-claim-court .grok/skills/
# and/or .claude/skills/
```

## What this is not

- Not a stock tip service (investment-claim-court **refuses** buy/sell advice)
- Not a live trading bot
- Not a substitute for OS schedulers (worker skill documents the pattern; you still need launchd/cron/systemd + scripts in *your* repo)
- Not “same model LGTM = independent review”

## Dual-agent decisions

Exactly one of:

- **ACCEPT** — bounded proceed  
- **REVISE** — one correction round max  
- **HUMAN_REQUIRED** — secrets, money, live, irreversible, or second disagreement  

`HUMAN_REQUIRED` cannot be self-cleared by the same agent family.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

Software and process templates only. **Not financial advice.** No warranty. You are responsible for how agents run on your machines and with your capital.

## Origin

Extracted as a portable pack from personal research/ops practice. If you use these in production agent fleets, keep allowlists tight and fail closed.
