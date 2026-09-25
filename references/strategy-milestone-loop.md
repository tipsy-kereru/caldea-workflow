# Milestone automation loop — proposed strategy (PROPOSAL, not yet validated)

User's target loop: 지시 → 마일스톤 개발 → 검증 → 커밋 → PR 리뷰 → 개선 → 재검증 → 다음 마일스톤, with Slack progress reports. Status: designed in conversation, NOT built. Do not present as a working workflow.

## Idea sources mapped to the user's stack

From the Lauren Tan / GrokBot report (in `~/kereru-studio/references/`):

- **Trust curve:** low-trust/high-intervention → build verification skills → gradually widen automation → PR auto-merge with human reviewing only major PRs. Apply as phases, not all at once.
- **Strong vs weak constraints (the load-bearing idea):** AGENTS.md rules/skills are WEAK constraints agents forget; CI/lint/typecheck/tests are STRONG constraints. The loop is only fully automatable where every gate is machine-checkable. Promote repeated review findings into lint/CI rules.
- **Verification skill + Feature Map:** agent must run/control the app itself (CDP traces); a Feature Map file teaches agents how to reach every feature. In this stack, mnemosyne's wiki+graph serves as the shared Feature Map.
- **PStack skill ops:** observe failure modes → codify as markdown skill; skills themselves get Evals (blind sub-agent testing + judge agent).
- **Head-chef model:** user directs once; orchestrator owns the DAG from then on.

## What already exists (loaded/verified skills)

- `orca-review-cycles` — the review→fix→re-review convergence loop, verdict format (PASS/CONDITIONAL PASS/REQUEST CHANGES), 3-round escalation rule, gate-approval template, commit-on-PASS discipline. This IS the PR리뷰→개선→재검증 segment.
- `orca-workspace-pitfalls` — verification standard, 3-party race detection (worker self-report + reviewer verdict + coordinator disk check), worker brief template (diff stat + mtime), commit pattern, proactive-orchestrator rule.
- `codex`, `test-driven-development`, `systematic-debugging`, `github-pr-workflow`, `requesting-code-review` — dev/PR segments.

## Missing pieces

1. **`milestone-loop` skill** — the full state machine: instruction intake → milestone selection → implement (worker dispatch) → verification gate (machine-checkable DoD commands) → commit → PR → review cycle → fix → re-verify → next milestone → Slack report. Entry/exit conditions, round caps, escalation, Slack reporting points (stage completion + periodic heartbeat).
2. **AGENTS.md workflow contract** — milestone DoD as explicit verification commands, commit format, worker_done report fields (diff stat + mtime), memory-tool routing (ai-memory = handoff/session recall; mnemosyne = codebase structure queries).

## Phase plan

1. Mechanize gates: fix each milestone's DoD as CI commands (typecheck/tests/build/E2E). Human reviews only.
2. Automate review loop: orca-review-cycles pattern, read-only reviewer agent, 3-round cap, commit on PASS, Slack heartbeat.
3. Auto-merge PR: only when gates are strong (CI) and reviewer converges PASS; failure patterns get promoted into skills (PStack method).
4. Eval the orchestration skills themselves.

## Memory layers inside the loop

- **ai-memory (short-term, continuity):** handoff at every session end → next worker/harness resumes with "where we left off"; survives milestone-spanning sessions and worker crashes. Ops rules: `finalize-session` for Codex/agy workers; wrap Orca tab commands with `ai-memory run <harness>`; decisions stay in session wiki via `memory_write_page` when explicitly asked.
- **mnemosyne (long-term, codebase knowledge):** pre-flight `mnemosyne add . --domain coding` per milestone; workers query the graph instead of guessing structure; PostToolUse hook keeps wiki in sync; confirmed design decisions from review cycles get promoted as entities. Restricted sources stay out.

## Key risk (from the reference report)

Weak constraints + fast conveyor belt = high-quality garbage. Gates must be CI-failing checks, not prose rules, before automation scope widens.
