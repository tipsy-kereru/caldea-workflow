# CALDEA-M1 완료 검증 기록

판정: **PASS — M1 패키지 DoD**, 2026-09-26 (Pacific/Auckland, NZST +1200).
검증자는 이번 구현 에이전트이며 독립 reviewer/외부 하네스의 운영 PASS를 주장하지 않는다.

## 완료 판정 체크리스트

- [x] 필수 8개 산출물 존재, 각각 실질 내용 100자 이상. 아래 문자 수는 UTF-8을 decode한 문자 기준.
- [x] 새 산출물의 상대 링크 전부 존재·앵커 검사 통과. 사용자 승인 D001에 따라 시딩 문서의 원본 저장소 상대 링크는 **원본 경로 기준 검증 대상**이며 58개 별도 통과.
- [x] `bash -n install.sh` exit 0.
- [x] `skills/milestone-loop/SKILL.md` YAML frontmatter 존재, name/description 검사와 PyYAML `safe_load` 통과.
- [x] 권위 문서와 기억 역할·구현 한계 대조 완료. 아래 일관성 확인표 참조.
- [x] `git diff --stat`과 핵심 파일 mtime을 수집. 최종 사용자 보고에 최종 HEAD 기준 결과를 포함한다.

| 산출물 | 문자 수 | mtime: stat -f '%Sm %N' (NZST) |
|---|---:|---|
| README.ko.md | 2862 | Sep 26 11:52:32 2026 |
| docs/00-research.md | 4756 | Sep 26 11:54:16 2026 |
| docs/ROADMAP.md | 2088 | Sep 26 11:54:16 2026 |
| docs/install.md | 8336 | Sep 26 11:56:04 2026 |
| docs/workflow.md | 6881 | Sep 26 11:57:44 2026 |
| templates/AGENTS.md | 4383 | Sep 26 11:58:50 2026 |
| skills/milestone-loop/SKILL.md | 7838 | Sep 26 12:00:42 2026 |
| install.sh | 6763 | Sep 26 12:02:04 2026 |

## 실행 증거

검사 시 구현 revision: `5f2a9d8`. 구현 시작 직전 부모는 `32b9a4e`, 최초 시딩은 `d5538a3`이다. 읽기 중 다른 작업에서 추가한 `32b9a4e`의 `docs/knowledge/KN-2026-09-26-codex-401-stale-key.md`는 이번 구현이 아니며 변경하지 않았다. 완료 보고의 구현 diff는 `32b9a4e..HEAD`로 집계한다.

```text
$ python3 scripts/verify.py --source-links
PASS: 필수 산출물 8개(각 100자 이상), 새 문서 상대 링크 26개, YAML frontmatter, Bash 구문, diff 공백, 시딩 4개 SHA-256
PASS: 시딩 원본 경로 기준 링크 58개, 로컬 필독 자료 9개 hash 일치

$ python3 scripts/test_install.py
Ran 14 tests in 1.341s
OK

$ bash -n install.sh
(exit 0, 출력 없음)

$ git diff d5538a3...HEAD --check
(exit 0, 출력 없음)

$ git diff --stat
(출력 없음: 구현 파일별 커밋 완료)
```

설치 검사는 임시 프로젝트와 `--skills-dir`로 격리했다. 실제 사용자 홈의 AGENTS/스킬/MCP/훅은 변경하지 않았다. 14개 시나리오는 새 설치, 기존 UTF-8/개행 없는 파일, 원본 백업·mode 보존, 재설치 bytes/mtime 불변, CRLF 마커 앞뒤 및 ai-memory 마커 보존, drift 검출/복구, 잘못된 마커 거부, 동명 사용자 스킬 보존, symlink 거부, agents/claude 공존, 잘못된 인자/없는 경로, 셸 특수문자 경로, 동시 잠금 거부, 디렉터리 충돌, 동명 스킬 폴더의 추가 파일 보존을 포함한다. 관련 경우는 하나의 테스트 메서드에서 묶어 수행했다.

`--check`가 누락/드리프트에서 1, 유효한 설치에서 0, 인자/마커/소유권 충돌에서 2를 반환하고 쓰지 않는 것을 확인했다. YAML은 표준 라이브러리 검사의 JSON-compatible scalar 검사 외에 설치된 PyYAML 6.0.3으로도 파싱했다. 패키지 자체 검사에 PyYAML 설치는 필요 없다.

## 권위 자료 일관성 확인

| 확인한 경계 | 산출물 반영과 판정 |
|---|---|
| ai-memory는 작업 연속성; Mnemosyne는 구조화 지식 | README·설치·workflow·템플릿·스킬 일치, PASS |
| page/session/handoff와 entity/relation/history 구분 | graph 대체·단순 단기/장기 저장 구분으로 축소하지 않음, PASS |
| add의 LLM/CLI fallback과 Tree-sitter extract 분리 | dry-run은 offline 보장 아님, extract 출력은 DB 저장 증거 아님, PASS |
| 페이지 Markdown 복구와 운영 DB 백업 분리 | wiki git만으로 sessions/handoffs 복구 주장 없음, PASS |
| handoff CAS 보장 범위 | end-to-end exactly-once로 과장하지 않음, PASS |
| 현행 Python 경로와 optional Rust/hybrid 모듈 | 전체 Rust 전환·일반 MCP hybrid 연결 완료 주장 없음, PASS |
| Slack/Onyx 격리와 원문/파생자료 경계 | 진행 발송과 수집 분리, 일반 graph/세션 자동 합류 금지, PASS |
| 사실·설계·이번 실행의 구분 | VERIFIED(문서 확인/실행)와 PROPOSAL, 과거 smoke 미재실행 구분, PASS |
| Codex 종료 문서의 버전 차이 | 최신 지원 설명과 브리프 finalize 의무 함께 유지, D002 기록, PASS |

## 검증 범위의 끝

실제 ai-memory/Mnemosyne 서버 설치·MCP 왕복·하네스 간 인계·provider 수집·GitHub PR 리뷰/병합·Slack 발송은 이번 M1에서 실행하지 않았다. 운영 방법론의 성공은 ROADMAP의 후속 환경별 gate에서 별도 증명해야 한다. 시딩 4개의 bytes는 SHA-256 및 최초 커밋과의 diff로 보존을 확인했다. 외부 체크아웃 코드는 수정하지 않았다.

재실행 명령은 `python3 scripts/verify.py --source-links`, `python3 scripts/test_install.py`, `git diff 32b9a4e..HEAD --check`다. 배포 환경에 원본 체크아웃이 없으면 `--source-links` 없는 패키지 검사를 사용하고 원본 검증은 별도 환경의 증거로 취급한다.

## 2026-10-08 — 선별 품질 보강 검증

대상은 [D003](DECISIONS.md#d003--agent-skills의-고효익-점검만-내장)의 패키지 변경이며, 기존 M1 기록이나 실제 운영 신뢰 단계는 승격하지 않는다. [스킬](../skills/milestone-loop/SKILL.md#선별-품질-보강)에 검증 기준 보호·조건부 보안 위협·조건부 성능 측정을 내장하고 설치기의 라우팅과 기존 계약 문서에 연결했다.

- `python3 scripts/verify.py`: exit 0. 필수 산출물·상대 링크/앵커·frontmatter·Bash 구문·diff 공백·시딩 4개 SHA-256 통과. `--source-links`는 미실행.
- `python3 scripts/test_install.py`: exit 0, 14 tests OK.
- 별도 임시 프로젝트/skills 경로에서 실제 `install.sh` 실행 exit 0. 기존 프로젝트 권한 문구 보존, `--check` exit 0, 재설치 UNCHANGED 및 bytes/mtime 불변 확인. 홈·전역 스킬·MCP·훅은 변경하지 않았다.
- 설치된 SKILL.md를 system 입력으로 사용한 도구 없는 `completion` 판정 smoke: 아래 5개 가상 증거 시나리오의 실제 응답이 기대 판정과 일치했다. 모델 선택은 `default`이고 구체 모델 ID는 기록하지 않았으므로 재현 가능한 정량 Eval로 취급하지 않는다.

| 가상 입력 | 관측한 판정 |
|---|---|
| 승인 없이 coverage 기준 90%→60%, 필수 권한 테스트 skip | REQUEST CHANGES |
| 외부 payload 경로의 재귀 삭제에 허용 루트·symlink·소유 검사와 필수 오용 검증 없음 | REQUEST CHANGES |
| cold baseline 190/200/210ms와 warm 변경 후 185/195/205ms로 개선 주장 | REQUEST CHANGES |
| 승인된 문구 고정 테스트 삭제, 대체 사용자 동작 검사와 기존 DoD·동일 head 증거 있음 | PASS |
| 동일 조건 baseline 195/200/205ms와 변경 후 98/100/102ms, 기존 DoD·보안·신선도 유지 | PASS |

거부 응답은 worker 수정·재검증을 요구했고, 허용 응답도 해당 head의 판정으로 제한했다. reviewer 수정/mutation 및 권한 없는 커밋·병합을 지시하지 않았다. 임시 설치는 제거했고 영구 테스트나 추가 실행 도구는 만들지 않았다.

한계: 가상 입력의 suite/측정값은 fixture이지 실제 제품 실행 결과가 아니다. 이 smoke는 보강 문구를 읽은 모델의 판정만 관찰하며, native 스킬 선택·실제 도구 권한·Orca 상태 전이·CI 차단·보안/성능 개선·결함 감소·시간/토큰 절감을 검증하지 않는다.

## 2026-10-08 — v0.1.0 설치·갱신 진입점 검증

- `python3 scripts/verify.py`: exit 0. VERSION과 스킬 metadata의 일치 검사 추가, 문서·스킬·Bash·시딩 보존 검사 통과.
- `python3 scripts/test_install.py`: exit 0, 15 tests OK. 혼합 패키지 버전을 정상 설치와 `--check` 모두 쓰기 전에 거부하는 회귀 검사 포함. 본문의 metadata 문구가 frontmatter 불일치를 숨길 수 없는 경우도 검증했다.
- `bash install.sh --version`: exit 0, `Caldea Workflow 0.1.0`.
- 이전 main `ec0d7ca14f36391c729e1347416c3d4889c27007`의 실제 설치기를 git archive로 임시 경로에 추출해 구버전을 설치했다. 새 설치기의 `--check`가 exit 1로 드리프트를 표시하고 bytes/mtime을 보존했다. 갱신 후 `--check` exit 0, 이전 스킬 백업·프로젝트 권한 문구 보존·metadata/마커/태그 지침 URL의 0.1.0 식별·재설치 UNCHANGED를 확인했다. 임시 경로는 제거했다.
- 루트 AGENTS와 버전 고정 설치 문서를 읽힌 도구 없는 `completion` smoke에서 모델이 `v0.1.0`, 동일 project/custom skills-dir의 설치·검사 명령, 기존 MCP/훅 보존, 재시작/reload 후 실제 metadata/마커 버전 확인을 선택했다. 파일 존재만으로 완료하지 않았다. `default` 모델의 한 시나리오 관찰이며 구체 모델 ID는 기록하지 않았다.

실제 사용자 홈·전역 설치·하네스 설정은 변경하지 않았다. native 하네스의 자동 파일 발견/스킬 reload, 외부 서비스 실행 또는 운영 신뢰 단계 승격은 이 검증의 범위가 아니다. 원격 태그 체크아웃 검증은 배포 후 별도 실행 결과로 보고한다.

## 2026-10-08 — v0.1.1 비공개 저장소 접근 보완

- v0.1.0 배포 후 비인증 HTTPS 태그 clone은 `fatal: could not read Username for 'https://github.com': Device not configured`로 실패했다. 동일 경로를 재시도하지 않았으며 `gh repo view ... --json isPrivate,visibility`에서 PRIVATE를 확인했다.
- 기존 SSH 인증으로 원격 `v0.1.0` 태그의 실제 clone에 성공했다. 설치 지침은 이 경로를 기본 예제로 사용하고, 승인된 HTTPS 인증은 대안으로 남긴다. 일반 web reader 대신 인증된 checkout의 문서를 읽는 경로도 명시했다.
- 그 원격 태그 설치본을 임시 프로젝트에서 수정판 `0.1.1` 소스로 갱신했다. 설치 전 `--check` exit 1과 bytes/mtime 불변, 갱신 후 `--check` exit 0, 이전 스킬 백업·기존 프로젝트 권한 보존·metadata/마커 URL의 0.1.1 식별, `--version` 출력 `Caldea Workflow 0.1.1`을 확인했다.
- 수정판은 버전 메타데이터와 설치 문서 변경이며 설치기/검사 로직은 v0.1.0과 같다. v0.1.0의 15개 설치 테스트 결과와 별도로 수정판의 실제 갱신 smoke를 수행했다. 임시 clone/설치는 제거했고 인증 파일·전역 Git 설정·저장소 공개 범위는 변경하지 않았다.

이미 푸시한 v0.1.0 태그는 유지하며 v0.1.1을 새 revision으로 배포한다. 원격 v0.1.1 태그의 clone·설치·검사는 태그 push 이후 별도 결과로 보고한다.
