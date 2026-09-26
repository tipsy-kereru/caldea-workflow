# KN-2026-09-26 — Orca 멀티 하네스 기억 공유·인계 시나리오

**상태:** VERIFIED(원리) + PROPOSAL(시나리오 절차) — 2026-09-26
**범위:** Orca를 통해 codex·OMP·Claude Code·agy 등 여러 하네스를 하나의 프로젝트에 섞어 쓸 때, 세션 기억을 잃지 않고 인계하는 운영 규칙. degaza-v2 실측(doctor: codex 16/16, omp 6/6 captured) 기반.

# 1. 설계 원칙 — 왜 하네스가 바뀌어도 기억이 남는가

- **기억의 소유자는 하네스가 아니라 ai-memory 서버**다. 모든 하네스가 같은 서버(기본 127.0.0.1:49374)에 MCP+훅으로 붙고, 기억은 `(workspace_id, project_id, path)` 3-tuple로 키잉된다. cwd와 `.ai-memory.toml` 마커로 스코프가 결정되므로 "어떤 하네스가 썼는지"는 기억의 키가 아니다.
- **authority는 기억이 아니라 디스크다.** 작업 상태의 정본은 Orca 증거·커밋·CI이며, ai-memory는 복구와 인계의 단서다(운영 매뉴얼 §프로세스 중단 규칙).
- **역할 분리**: 세션 인계·이전 결정 = ai-memory / 현재 코드 구조·호출 관계 = mnemosyne / 지휘·작업 분배 = Orca. 같은 질문을 이중 질의하지 않는다(AGENTS.md 기억 도구 라우팅 계약).

# 2. 하네스별 캡처 능력 차이 (install.md §3 기준)

| 하네스 | MCP | lifecycle 훅 | 세션 종료 규칙 |
|---|---|---|---|
| Codex | 있음 | 있음 | 마지막 턴 후 `finalize-session --agent codex --session-id <exact-id>` 확인. native 종료됐으면 종료·handoff 증거 기록 |
| OMP | 있음 (full) | TypeScript extension 훅 | 훅이 세션 경계 캡처 — 별도 finalize 의무 없음 |
| agy(antigravity-cli) | 있음 | 있음 (invocation 0만 시작 경계) | Codex와 동일 finalize 규칙 |
| Claude Code | 있음 | 있음 | 동시 세션이면 server `[auto_scope] mode="per_session"` + `--session-aware` bridge |

공통 전제: 프로젝트 루트에 `.ai-memory.toml` 마커가 있어야 캡처가 이벤트 단계부터 흐른다(마커 없으면 조용한 무캡처 — install.md 채택 필드 노트).

# 3. 전환 시나리오

## A. 정상 전환 — 하네스 A에서 B로 (예: codex → omp)

1. A 세션 마무리: handoff 작성 의뢰 — "현재 checkpoint·다음 행동·잔여 위험을 포함한 handoff 작성해줘".
2. Codex/agy면 `finalize-session --agent <harness> --session-id <exact-id>` 실행·확인(요약+handoff 생성까지). OMP는 세션 경계에서 자동.
3. B 하네스를 같은 프로젝트 dir에서 시작 → "이전 handoff 읽고 이어서 진행해줘" → handoff list→accept(claim-once, 한 번만 소비).
4. static MCP이므로 프로젝트 스코프 호출에는 정확한 `workspace`/`project`를 명시한다. 폴더명 추측·마지막 활성 프로젝트 의존 금지.

## B. 병행 운영 — 두 하네스 동시 사용

- **동일 workstream 동시 writer는 lease 충돌**한다. 역할별로 서로 다른 workstream 이름을 준다(예: `codex-impl` / `omp-reviewer`). 재개 시 `--workstream <name>`으로 동일 스트림에 계속한다.
- 공유는 page 단위: 구현 결과는 커밋+PR 증거로 남기고, 진행 상황은 각자 handoff/page로 기록해 상대가 읽게 한다.
- 병행 중 충돌 우려가 큰 변경은 오케스트레이션 계층(Orca orchestration task)에서 순서를 정한다. 기억 도구가 권한 승격·작업 조율의 근거가 되지 않는다.

## C. 크래시·강제 종료 후 복원

1. finalize 전에 죽었으면: `ai-memory backfill`로 로컬 하네스 세션 저장소를 흡수(재실행 no-op)하고 `ai-memory doctor`로 captured 여부 확인.
2. 마지막 유효 커밋·dirty diff·미완료 task·리뷰 round를 코드·로그에서 복원한다. ai-memory 인계와 현재 소스를 대조해 완료된 명령·커밋·PR을 재실행하지 않는다(운영 매뉴얼 규칙).
3. 복원 사실을 새 handoff로 기록해 다음 하네스가 같은 추정을 반복하지 않게 한다.

# 4. Orca 관점 결합 (workflow.md §실행 시작)

```bash
# 하네스마다 다른 workstream 이름 — lease 충돌 방지
orca terminal create --worktree id:<repo-id>::<absolute-path> \
  --title M1-worker --command 'ai-memory run --new M1-worker codex' --json
orca terminal create --worktree id:<repo-id>::<absolute-path> \
  --title M1-reviewer --command 'ai-memory run --new M1-reviewer omp' --json
```

- `ai-memory run`은 managed workstream(레저·ledger·resume)을 부여하는 래퍼다. 같은 스트림을 계속할 때는 `--workstream <name>`.
- codex desktop 앱(GUI)로 작업한 이력도 같은 로컬 세션 저장소를 공유하므로 backfill/doctor로 흡수·검증 가능하다. GUI와 CLI 하네스가 같은 프로젝트 기억을 읽는다.
- Orca의 orchestration(task-create/dispatch)은 지휘 채널이고 ai-memory는 기억 채널이다. worker_done 보고·dispatch receipt는 Orca 증거로, 인계 내용은 ai-memory로 각각 남긴다.

# 5. 합격 판정 (전환·공유가 작동하는지)

- `ai-memory doctor`: 프로젝트에서 최근 실행된 모든 하네스가 captured인지.
- 하네스 전환 후 새 하네스에서 실제 recall("이전 진행 불러와줘")로 handoff 수신 확인 — static MCP는 workspace/project 명시.
- `git log`·`git status`로 기억 내용과 디스크 상태 불일치가 없는지 대조. 불일치가 authority다.