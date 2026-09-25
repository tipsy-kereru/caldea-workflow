# ISSUE-CALDEA-001 — Caldea Workflow 패키지: 연구 + 리포 구현 (M1)

**역할:** 당신은 이 리포의 연구·구현 담당 워커다. 연구와 구현을 모두 수행한다.
**모델/페이로드:** gpt-6-astra, thinking high.
**산출물 검증:** 완료 시 반드시 `git diff --stat` 결과와 핵심 파일들의 mtime(`stat -f '%Sm %N' <file>`)을 완료 보고에 포함한다. (3-party 검증 규칙 — self-report는 리드일 뿐이다.)

## 목표 (큰 그림)

`/Users/kereru/Development/caldea-workflow`를 **"칼데아 워크플로우" 배포 패키지 리포**로 구축한다. 이 패키지는 다른 프로젝트에서 설치 가능한 형태로, 다음 전체 루프의 자동화 방법론을 담는다:

```
사용자 지시 → 마일스톤 개발 → 검증(기계 판정 게이트) → 커밋 → PR 리뷰
→ 개선 → 재검증 → 다음 마일스톤 → (중간중간 Slack 진행 보고)
```

멀티 에이전트 하네스(OMP, Codex 등) 위에서 Orca로 오케스트레이션하며, ai-memory(세션 연속성)와 mnemosyne(코드베이스 지식 그래프)이 루프 안에서 각자의 역할로 동작한다.

## 필독 자료 (구현 전 전부 읽기 — 절대 경로)

1. `references/source-lauren-tan-grokbot.md` — 원론: 신뢰 곡선, 강한/약한 제약, 검증 스킬, Feature Map, PStack 스킬 운영, 헤드 셰프 모델
2. `references/strategy-milestone-loop.md` — 마일스톤 루프 설계 제안 (아이디어→스택 매핑, Phase 계획, 리스크)
3. `references/strategy-memory-stack.md` — ai-memory/mnemosyne 로컬 체크아웃·와이어링 명령·하네스별 주의점
4. `references/authority-memory-comparison.ko.md` — 팀 공식 비교 문서: 두 기억 시스템의 역할 경계 (절대 권위 문서, 임의로 재해석 금지)
5. 로컬 체크아웃 참조 (설치 절차 인용용):
   - ai-memory: `/Users/kereru/Development/ai-memory/docs/{install.md,usage.md,mcp-install.md,managed-workstreams.md,support-matrix.md}`
   - mnemosyne: `/Users/kereru/development/mnemosyne/{README.ko.md,MANUAL.ko.md}` (§3.8 에이전트 연동)
6. 기존 검증 스킬 (패키지가 흡수/참조할 부품):
   - `/Users/kereru/.hermes/profiles/cto/skills/autonomous-ai-agents/orca-review-cycles/SKILL.md`
   - `/Users/kereru/.hermes/profiles/cto/skills/autonomous-ai-agents/orca-workspace-pitfalls/SKILL.md`
   - 스킬 작성 규격이 필요하면 `/Users/kereru/.hermes/profiles/cto/skills/software-development/hermes-agent-skill-authoring/SKILL.md` 참조

## 산출물 (M1 범위)

1. `README.ko.md` — 패키지 소개, 핵심 개념(신뢰 곡선, 강한/약한 제약), 빠른 시작
2. `docs/00-research.md` — 위 자료들의 연구 종합: 왜 이 설계인가, 아이디어→구성 요소 매핑
3. `docs/ROADMAP.md` — 4단계 신뢰 곡선 로드맵 (게이트 기계화 → 리뷰 루프 자동화 → PR 자동 병합 → 스킬 Eval). 각 단계의 진입/종료 조건과 완료 판정 방법을 명시
4. `docs/install.md` — 에이전트 하네스가 실행하는 설치 지침: ai-memory 서버+MCP+훅 (에이전트별: omp/codex/agy/claude — codex/agy는 `finalize-session` 규칙 필수), mnemosyne (pip, `add`, 훅, MCP, skill install), Orca 프로젝트 등록, 검증 절차 (`ai-memory status`, `mnemosyne config hook status`). 설치 스크립트가 아니라 "하네스에게 내리는 지침 문서" 형태로
5. `docs/workflow.md` — 마일스톤 루프 운영 매뉴얼: 상태 머신 (지시수신→마일스톤 선정→개발→검증게이트→커밋→PR→리뷰사이클→개선→재검증→다음 마일스톤), 상태 전이의 진입/종료 조건, 라운드 상한(리뷰 3라운드 규칙), 에스컬레이션, Slack 보고 시점(단계 완료 + 주기 하트비트), 사용하는 orca-cli 명령 (`terminal create`, `orchestration dispatch/check`, worker_done 계약)
6. `templates/AGENTS.md` — AGENTS.md 작성 가이드 + 채워넣기 템플릿: 마일스톤 DoD를 명시적 검증 명령(typecheck/테스트/빌드)으로 기술하는 법, 커밋 메시지 형식, worker_done 보고 필수 항목(`git diff --stat` + mtime), 기억 도구 라우팅(ai-memory=세션 인계, mnemosyne=코드 구조 질의 — 이중 질의 방지)
7. `skills/milestone-loop/SKILL.md` — 위 상태 머신 전체를 스킬로 (frontmatter 포함, 설치 가능 형태). orca-review-cycles의 수렴 루프와 pitfalls의 검증 표준을 통합·인용하되 자기완결적으로
8. `install.sh` — 패키지 설치기: 스킬을 `~/.agents/skills/` 또는 `~/.claude/skills/`에 복사, AGENTS.md에 마커 블록(`<!-- caldea-workflow:start -->`)으로 라우팅 스니펫 삽입(기존 내용 보존, 타임스탬프 백업), `--check` 모드

## 구현 순서 (분석 정체 방지 — 이 순서대로 바로 진행)

1. 자료 6종 읽기 (필독 1~4, 참조 5~6)
2. 리포 구조 확정 후 README.ko.md부터 순서대로 작성
3. 스킬 파일 → 템플릿 → install.sh → docs 순으로도 가능하되, 각 파일 완성 시점마다 커밋
4. 커밋 메시지: `feat(caldea-m1): <한국어 요약>` (문서만이면 `docs(caldea-m1):`)
5. 자체 검증 후 완료 보고

## 완료 판정 (DoD — 기계 판정 가능)

- [ ] 위 8개 산출물 전부 존재, 각 100자 이상 실질 내용
- [ ] 모든 상대 링크 깨지지 않음 (직접 확인)
- [ ] `install.sh` `bash -n` 통과
- [ ] skills/milestone-loop/SKILL.md에 YAML frontmatter 존재
- [ ] 모든 문서가 references/ 권위 문서와 모순 없음 (특히 기억 시스템 역할 경계)
- [ ] `git diff --stat` + 핵심 파일 mtime을 완료 메시지에 포함

## 제약

- 시크릿·API 키를 어떤 파일에도 쓰지 않는다
- 기존 파일(references/ 시딩 4개)은 수정하지 않는다
- 설계 제안과 검증된 사실을 구분해 표기한다 (PROPOSAL vs VERIFIED)
- 문서는 한국어 (코드/명령은 그대로)
- 이 브리프 범위 밖의 저장소(ai-memory, mnemosyne 코드)를 수정하지 않는다 — 읽기만