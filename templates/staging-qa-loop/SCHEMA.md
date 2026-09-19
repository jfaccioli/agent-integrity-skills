# Cycle report schema

`cycles/NNN/report.json`

```json
{
  "cycle": "001",
  "area": "auth",
  "started_at": "ISO-8601",
  "finished_at": "ISO-8601",
  "environment": "staging",
  "app_url": "https://staging.example.invalid",
  "git_sha_tested": "unknown-if-unreadable",
  "account": "staging-tester",
  "summary": {
    "p0": 0,
    "p1": 0,
    "p2": 0,
    "p3": 0,
    "enhancements": 0,
    "wontfix_false_positives": 0
  },
  "journeys_run": ["login", "primary-workspace"],
  "findings": [
    {
      "id": "AUTH-001",
      "area": "auth",
      "kind": "defect",
      "severity": "P1",
      "confidence": "high",
      "reproducible": true,
      "title": "Short title",
      "steps": ["1.", "2."],
      "expected": "",
      "actual": "",
      "prerequisites": "Logged-in staging tester",
      "screenshots": ["screenshots/auth-001.png"],
      "console": [],
      "network": [],
      "impact": "",
      "suggestion": "",
      "duplicate_of": null
    }
  ],
  "passed_checks": ["Session survives reload on the primary workspace"],
  "blocked": [],
  "notes": "Trust verdict: would a real user trust this staging journey? If no, name why and finding IDs."
}
```

`blocked` items may include `{ "reason": "<code>", "surface": "<area>", "copy": "..." }`.

Common `reason` values: `quota_gate`, `auth_expired`, `browser_tools_unavailable`, `git_push_blocked`, `environment_down`. A real quota or permission gate that stops a journey is not automatically a defect; dishonest copy around that gate is.

`notes` must include a one-line trust verdict for a real user of this product.

`kind` is `defect` or `enhancement`.
`severity` is `P0` | `P1` | `P2` | `P3`.
`confidence` is `high` | `medium` | `low`.

IDs are stable per area (examples: `AUTH-`, `NAV-`, `CORE-`, `UX-`). Reuse the previous ID and set `duplicate_of` for the same root cause.
