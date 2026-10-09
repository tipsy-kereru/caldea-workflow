# Caldea Workflow agent entry point

## Install or upgrade Caldea

- Read [docs/install.md](docs/install.md), starting with **0. 버전 고정 설치·갱신**, before installing or upgrading. Do not treat an implementation request as installation approval.
- [VERSION](VERSION) is the package version source. The release tag is `v<VERSION>`; use a pinned tag checkout rather than an unreviewed `main` update.
- Inspect the target project's existing rules, selected harness and actual skill directory. Preserve project authority and DoD; update only the installer-managed skill and Caldea marker.
- Run the installer and its read-only `--check` against the same target and skill directory. Restart/reload the selected harness and verify the loaded skill's `metadata.version` and the target AGENTS marker version. File presence alone is not installation completion.
- Updating the package does not authorize new MCP servers, hooks, global plugin installation, external data transfer or automatic merge. Keep working integrations unless separately requested.

## Work on this repository

- Read [README.md](README.md), [docs/DECISIONS.md](docs/DECISIONS.md) and the relevant implementation contract. The executable workflow lives in [skills/milestone-loop/SKILL.md](skills/milestone-loop/SKILL.md).
- Use the workflow's task-level `context_start` and `context_end` in the existing brief/report: verify current relevant context before a new task or resume, record the result and next action at completion, and reconcile evidence before dependent work. Reuse valid context within the task; refresh only affected inputs after external changes. Do not create per-tool memory reads or per-task session finalization.
- Before releasing, run `python3 scripts/verify.py` and `python3 scripts/test_install.py`, and exercise an isolated install/upgrade with `--skills-dir`. Preserve seeded reference documents.
- Keep VERSION, skill metadata, its version-pinned install link and release documentation consistent. Record changes in [CHANGELOG.md](CHANGELOG.md). Commit/push/tag only when requested.
- This root file guides agents working on the Caldea package. Do not copy it over another project's AGENTS.md; use `install.sh` and [templates/AGENTS.md](templates/AGENTS.md).
