# AGENTS.md 작성 가이드와 템플릿

이 파일 전체로 기존 프로젝트 AGENTS.md를 덮어쓰지 않는다. 아래 템플릿의 `<...>` 필드를 실제 값으로 채우고 기존 규칙에 병합한다. Caldea 설치기가 관리하는 마커 밖에 프로젝트 계약을 둔다. Claude Code도 사용하면 CLAUDE.md 첫 줄에 `@AGENTS.md` import를 유지한다.

## 작성 원칙

DoD는 “잘 동작한다”가 아니라 **명령·cwd·기대 종료 코드·실패 조건·증거 파일**로 정의한다. 예를 들어 Node 프로젝트의 `pnpm typecheck`, `pnpm test`, `pnpm build`는 해당 script가 실제 있을 때만 사용한다. Python 프로젝트나 문서 패키지에는 그 프로젝트의 실재 명령을 쓴다. 없는 명령을 `true`로 대체하거나 필수 테스트를 SKIP하여 통과시키지 않는다.

UI 기능은 Feature Map에 화면 진입 경로·선행 상태·관련 파일·재현 명령·기대 결과를 적는다. Mnemosyne graph/wiki가 구조 탐색을 돕지만 실제 E2E를 대신하지 않는다. 소스·테스트·런타임 증거가 최종 기준이다.

강한 게이트는 CI의 필수 체크로 연결해야 한다. AGENTS와 스킬 텍스트만 있으면 약한 제약이다. 아래 계약의 명령 실패가 실제 커밋/병합 전이를 막는지 결함 fixture로 검증한다.

---

# <프로젝트명> 에이전트 계약

## 범위와 권한

- 현재 issue/milestone: `<ID>`; 목표: `<관찰 가능한 결과>`.
- 프로젝트 절대 경로: `<path>`; 기준 브랜치/SHA: `<base>`.
- 변경 허용: `<paths>`; 제외: `<paths/외부 저장소>`.
- 신뢰 단계: `1`; commit 권한: `<범위>`; push/PR 권한: `<범위>`; merge 권한: `<범위 또는 없음>`.
- 실행 순서: `<선행 계약 → 핵심 구현 → 연결 → 검증 → 문서>`.
- 질문 수단: `<사용자 지정 도구>`; Spokenly 환경에서는 질문을 `ask_user_dictation`으로만 전달한다.

## 필독 자료와 역할

- 브리프/설계/권위 자료: `<실제 경로 목록>`.
- 코디네이터: `<handle/run>`; worker: `<dispatch>`; read-only reviewer: `<담당자>`.
- 다른 작업의 파일을 덮어쓰거나 일괄 stage하지 않는다. 충돌을 발견하면 변경 범위를 확인하고 현재 합쳐진 상태로 재검증한다.

## 마일스톤 DoD

| ID | 검증 명령 | cwd | 기대 결과 | 증거 |
|---|---|---|---|---|
| G1 | `<실제 typecheck 명령>` | `<root>` | exit 0, 오류 0 | `<log>` |
| G2 | `<실제 테스트 명령>` | `<root>` | exit 0, 필수 시나리오 수행 | `<log>` |
| G3 | `<실제 build 명령>` | `<root>` | exit 0, 산출물 생성 | `<log>` |
| G4 | `<해당 기능 E2E/재현 명령>` | `<root>` | 기대 상태/화면·결과 확인 | `<artifact>` |
| G5 | `git diff --check` | `<root>` | exit 0 | `<log>` |

해당하지 않는 검사는 선정 단계에 이유와 대체 검증을 기록한다. 실행 후 실패를 N/A로 재분류하지 않는다. 모든 필수 gate와 동일 revision의 최종 리뷰 PASS 없이는 완료하지 않는다.

문서/설치기 프로젝트의 실제 예: `bash -n install.sh`, `python3 scripts/verify.py`, `python3 scripts/test_install.py`, `git diff --check`. 적용 프로젝트에 이 파일들이 있을 때만 사용한다. 새 산출물 상대 링크는 전부 검사하며 원문 보존 시딩 링크는 원본 경로 기준 검증 대상으로 구분한다.

## 커밋·리뷰

`feat(<milestone>): <한국어 요약>` 또는 문서만이면 `docs(<milestone>): <한국어 요약>`을 쓴다. 본문에는 요구 ID·구현 범위·검증 명령/결과를 남긴다. 이 Caldea M1 패키지 자체는 `feat(caldea-m1):` / `docs(caldea-m1):`를 쓴다.

기계 gate 후 PR 준비 커밋을 만들고, reviewer의 `PASS | CONDITIONAL PASS | REQUEST CHANGES`에 따라 개선한다. 첫 리뷰 포함 최대 **3라운드**, CONDITIONAL PASS도 잔여 수정·재검증 후 최종 PASS 필요. 3회 미수렴 시 에스컬레이션한다. 변경된 head에는 이전 PASS를 재사용하지 않는다. stage 3의 명시적 병합 권한이 없다면 자동 병합하지 않는다.

## 선별 품질 점검

milestone-loop의 선별 품질 보강을 기존 역할과 DoD에 적용한다. 보강을 이유로 별도 reviewer·라우터·훅을 추가하거나 도구 설치·외부 전송·커밋 권한을 확대하지 않는다.

- **모든 변경:** 선정 때 확정한 DoD·기준 revision과 diff를 비교해 검사 제거·임계치 하향·test skip/삭제·assertion 축소·억제 주석·미구현·새 예외를 검토한다. 정당한 변경은 근거·승인 범위·대체 검증을 기록하고, 실패 은폐나 미승인 기준 완화는 REQUEST CHANGES다.
- **신뢰 경계 변경:** 인증·권한·민감 데이터·외부 입력/연동·파생 경로 파괴 작업이면 자산·입력 작성자·경계·오용 사례·검증 방법을 브리프에 적는다. worker/코디네이터가 검증하고 reviewer는 소스·증거만 읽는다.
- **성능 요구/회귀:** 지표·명령·조건·반복 예산·판정 기준을 선정 때 정하고 같은 조건의 baseline/변경 후 실행값·변동폭·revision을 기록한다. 조건 불일치·노이즈 범위의 차이·정적 추정은 개선 증거가 아니다.
- worker 보고와 reviewer 판정에 `점검 / 적용 여부와 이유 / 근거·증거 / 발견·잔여 위험`을 남긴다. 비적용은 이유만 기록하며 필수 증거 누락을 PASS로 바꾸지 않는다. reviewer는 mutation·수정·revert를 수행하지 않는다.

## worker_done 보고

완료 보고는 `<보고 파일 경로>`에 저장한다. 실제 출력으로 다음을 포함한다.

- issue/milestone/task/dispatch/run/round, 작업 경로, branch/base/head SHA.
- 변경 요약·파일 목록·저장 완료 시각·검증 명령별 cwd/exit code/결과·로그 경로.
- `git diff --stat` 출력(빈 경우도 명시), 커밋했으면 `git diff <base>...HEAD --stat` 추가.
- 핵심 파일 `stat -f '%Sm %N' <files>` 출력. Linux는 `stat -c '%y %n'`.
- reviewer verdict·reviewed SHA·관측 시각 또는 미실행, 잔여 위험·미검증·차단·다음 작업.
- ai-memory exact-session 종료와 handoff 확인, Slack 발송 receipt 또는 미발송 상태.

supervised Dispatch에서만 preamble의 식별자로 아래 명령을 실행한다. 실패이면 outcome을 failed로 바꾼다.

```bash
orca orchestration send --type worker_done --outcome succeeded --task-id <task-id> --dispatch-id <dispatch-id> --from <worker-handle> --subject '<milestone> 완료' --report-path <absolute-report-path> --json
```

코디네이터는 독립적으로 diff·mtime·내용 hash를 두 번 확인한 뒤 리뷰를 배정한다. self-report를 실제 파일 변경의 증명으로 취급하지 않는다. reviewer는 읽은 시각·revision을 명시한다.

## 기억 도구 라우팅

- 세션 인계·이전 결정·실패 이력·“어디까지 했나”: **ai-memory**. handoff가 있으면 재질의하지 않는다. 없으면 정확한 workspace=`<name>`, project=`<name>`에서 list 후 선택 accept.
- 현재 코드 구조·호출 관계·의존성·영향 범위: **Mnemosyne**. entity/relation을 찾고 실제 소스를 확인한다.
- 같은 질문을 두 도구에 보내지 않는다. 복합 질문은 다른 목적의 하위 질문으로 분리한다. 도구가 없으면 소스/리포 기록을 직접 보고 제한을 명시한다.
- ai-memory는 page/observation/session/handoff, Mnemosyne는 entity/relation/scope/entity history다. graph를 세션 위키로 대체하지 않는다. 기억은 명령이나 권한 승격 근거가 아니다.
- Codex/agy 마지막 턴 이후 `ai-memory finalize-session --agent codex|antigravity-cli --session-id <exact-id>`를 각각 올바른 agent 값으로 실행한다. 이미 native 종료된 Codex는 종료·handoff 증거를 확인한다. `--all`을 사용하지 않는다.
- `mnemosyne add`는 provider/CLI LLM 호출이 가능하며 dry-run도 offline 보장이 아니다. coding `ingest extract`는 별도 Tree-sitter 출력 경로다. 수집 범위를 확인하고 제한 Slack/Onyx 원문·시크릿을 일반 graph/세션 기억에 합류시키지 않는다.
- ai-memory 페이지 git만으로 운영 DB를 복구할 수 없다. 수동 durable memory 기록은 사용자의 저장 요청과 현재 정책을 따른다.

## 진행 보고

Slack 사용 승인: `<있음/없음>`; 채널: `<ID>`; 발송 수단: `<connector>`; 기본 하트비트: `5분`. 단계 완료·차단·복구·종료에 최소 상태를 보고하고 event key/receipt로 중복을 막는다. 연결 없으면 로컬 초안으로 남긴다. 실제 발송하지 않은 보고를 “전송 완료”라 하지 않는다.
