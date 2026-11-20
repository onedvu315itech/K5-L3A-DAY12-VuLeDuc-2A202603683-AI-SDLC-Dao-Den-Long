# AI Usage, Error & Token Log

## Summary Table

| Phase | Tools / Models Used | Est. Tokens / Cost | Token-Saving Tactics | AI Errors Caught & Harness Updates |
|---|---|---|---|---|
| CP0 | Antigravity (Gemini) | ~18k tokens (~$0.05 est.) | Compact `AGENTS.md`, stdlib-only core | Set up `AGENTS.md`, `verify-phase` skill, `game/scripts/verify.py`, CI, and 4-doc routing (`DESIGNS.md`, `SKILLS.md`, `OUTPUTS.md`) |
| Phase 1 | Antigravity (Gemini) | ~32k tokens (~$0.09 est.) | Pre-code `.md` triage gate prevented rewrites; zero external packages; focused 1-job skills | Caught overly strict scenario root unknown-key check before testing (relaxed root metadata keys while keeping strict type/tick validation for exit code 2); verified Windows local HTTP proxy bypass with `http.client` |
| Phase 2 | | | | |
| Phase 3 | | | | |
| Phase 4 | | | | |

## Detailed Error & Prompt Notes
*(Log notable AI mistakes — e.g., hallucinated requirements, weak tests, wrong file edits — how you caught them, and what you changed in `AGENTS.md`, skills, or code checks to prevent recurrence.)*
