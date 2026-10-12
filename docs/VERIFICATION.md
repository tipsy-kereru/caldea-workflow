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

## 2026-10-09 — v0.1.2 작업 맥락 체크포인트

- `context_start`: 기준 `2fab1c749dea20ca64737881f949460dd20d62f0`의 사용자 요청·루트 AGENTS·기존 스킬/설치기·템플릿·workflow·설치/변경/결정/검증 기록을 확인했다. 범위는 기존 작업 계약의 경량 보강, 패치 배포, 현재 하네스 관리 스킬 갱신이다. 새 MCP·훅·기억 backend나 다른 프로젝트 설정 변경은 제외한다.
- `python3 scripts/verify.py`: 최초 실행에서 DECISIONS의 EOF 공백 실패를 확인하고 제거했다. 수정 후 exit 0, 산출물 8개·문서 상대 링크 71개·frontmatter/version·Bash 구문·diff 공백·시딩 4개 SHA-256 통과. `--source-links`는 미실행.
- `python3 scripts/test_install.py`: exit 0, 15 tests OK. `bash install.sh --version`: exit 0, `Caldea Workflow 0.1.2`.
- 실제 `v0.1.1` 태그 설치기를 git archive로 임시 경로에 추출해 설치한 뒤 `0.1.2` 소스로 갱신했다. 설치 전 `--check` exit 1과 bytes/mtime 불변, 갱신 후 `--check` exit 0, 구버전 스킬 백업·프로젝트 권한 문구 보존·스킬/마커의 체크포인트 배포·0.1.2 metadata/태그 URL·재설치 bytes/mtime 불변을 확인했다. 임시 경로는 제거했다.
- 실제 설치된 스킬을 system 입력으로 사용한 도구 없는 `completion` smoke에서 아래 네 가상 입력의 응답을 관찰했다. 모델 선택은 `default`이고 구체 모델 ID는 기록하지 않았으므로 정량 Eval로 취급하지 않는다.

| 가상 입력 | 관측한 행동 결정 |
|---|---|
| 재개 시 handoff 기준과 실제 head 불일치, 다른 worker의 같은 파일 변경 | 영향 자료 재확인·충돌 작업 보류·context_start 갱신; handoff 재수락 없음 |
| 같은 task의 맥락·revision 유효, 외부 관련 변경 없음 | 기존 맥락 재사용; 다음 도구 호출마다 전체 기억 조회 없음 |
| 구현/DoD 증거는 있으나 context_end 보고 누락 | 완료 및 후속 의존 task 보류; 독립 task는 자체 시작 조건 확인 후 계속 |
| 기억 backend 없는 read-only reviewer, 필수 DoD 실패 | 브리프/소스로 한계 명시·BLOCKED 종료 판정 응답 제출·코디네이터 연결; 공유 수정/작업별 finalize 없음 |

- `context_end`: 결과는 VERSION `0.1.2`의 스킬·관리 마커·템플릿·운영 계약·배포 안내 보강이다. 검증 근거와 결정은 이 보고 및 [D005](DECISIONS.md#d005--작업-단위-맥락-체크포인트)에 남긴다. 다음 행동은 같은 변경 revision의 커밋·push·새 태그와 게시된 태그의 실제 설치/현재 관리 스킬 갱신이며, 그 결과는 배포 완료 보고에서 확인한다.

한계: 이 패키지는 하네스 운영 계약이다. 가상 입력의 증거는 fixture이며 smoke는 지침을 읽은 모델의 응답만 증명한다. native 자동 발견/reload·Orca 상태 전이 강제·CI·실제 기억 서버 실행·운영 비용/결함 감소를 증명하지 않는다. 매 작업의 기억 서버 쓰기나 세션 종료도 추가하지 않았다.

## 2026-10-13 — v0.2.0 응답 표현 스킬 통합

- `context_start`: clean `main` 기준 `0322ca7`에서 사용자 요청·루트 AGENTS·README·설치 계약·스킬·설치기·테스트·결정/검증 기록을 대조했다. upstream `ayghri/i-have-adhd`의 `1ecea1993b7fce257ffbd686c070948b5e07eda6` SKILL과 MIT LICENSE를 확인했다. 범위는 한국어 Caldea 응답 스킬·설치/AGENTS 연결·설치 지침·버전 갱신·커밋/push이며 다른 프로젝트 규칙·MCP·훅·플러그인·자동 병합 변경은 제외한다. 정확한 프로젝트 기억 scope를 선언한 marker가 없어 global 기억 검색을 사용했으나 관련 결정 근거는 얻지 못했으며 현재 소스와 리포 기록을 기준으로 삼았다.
- `python3 scripts/verify.py`: exit 0. 필수 산출물 10개·상대 링크 80개·두 스킬의 frontmatter/version·Bash 구문·diff 공백·시딩 4개 SHA-256 통과. `--source-links`는 미실행이다.
- `python3 scripts/test_install.py`: exit 0, 23 tests OK. 두 번째 스킬/라이선스 드리프트·복구·백업·mode 보존, 비관리 동명 스킬/라이선스-only 충돌의 쓰기 전 거부, 누락/빈 source LICENSE, 두 스킬 혼합 버전, symlink 충돌 및 기존 설치 계약을 검사했다. `bash install.sh --version`: exit 0, `Caldea Workflow 0.2.0`.
- 실제 `v0.1.2` 태그를 git archive로 임시 경로에 추출해 설치한 뒤 `0.2.0` 설치기로 갱신했다. 갱신 전 `--check` exit 1과 bytes/mtime 불변, 갱신 후 `--check` exit 0, 두 스킬 metadata 0.2.0·동봉 MIT LICENSE 일치·이전 스킬 백업·프로젝트 권한 문구 보존·재설치 UNCHANGED와 bytes/mtime 불변을 확인했다.
- 같은 격리 스킬 루트를 사용해 리포 자체 AGENTS의 관리 블록을 준비하고 `--check` exit 0을 확인했다. 기존 리포 계약을 그대로 보존했다. 이 준비 과정은 사용자 홈의 스킬을 바꾸지 않았고 준비용 AGENTS 백업은 보존 내용을 확인한 후 제거했다.
- 임시 설치된 응답 스킬과 AGENTS를 system 입력으로 읽힌 도구 없는 `completion` smoke를 수행했다. `default` 모델 선택이며 구체 모델 ID는 기록하지 않았으므로 정량 Eval로 취급하지 않는다.

| 가상 입력 | 실제 응답에서 관측한 결과 |
|---|---|
| 원인 미확인인 일곱 검증 실패의 전체 보고 요청 | 7개 명령·exit·실패를 모두 표에 표시, 원인 미확인 유지, 완료 판정 거부, 다음 조사 행동 하나 |
| exit 0/1/2와 0.1.2→0.2.0 갱신/로드 차이의 상세 설명 요청 | 짧은 목록 제한으로 설명을 자르지 않고 제목·단계·표로 설명, 가상 결과임을 명시, 파일 설치/검사/실제 로드 증거를 구분 |
| `normal mode`, 번호 없이 한 문장 확인 요청 | 일반 문단 응답과 명시적 재요청 전 비활성화를 한 문장으로 확인 |

- `context_end`: 결과 VERSION `0.2.0`에서 두 스킬과 LICENSE·관리 AGENTS·템플릿·설치/운영 안내를 통합했고 [D006](DECISIONS.md#d006--이해하기-쉬운-응답-표현-스킬-배포)에 출처·권한 경계를 기록했다. 다음 행동은 같은 revision의 커밋·annotated tag·원격 push, 게시된 태그의 실제 checkout/설치/검사 및 요청한 현재 하네스 스킬 갱신이다. 배포와 실제 설치 결과는 최종 응답에 별도로 기록한다.

한계: 모델 smoke는 가상 입력에 대한 지침 적용 관찰이지 native 스킬 자동 발견/reload·세션 간 지속성·실제 이해도 개선의 증거가 아니다. 실제 하네스 재시작 및 두 스킬의 새 세션 로드는 파일 검사와 분리해 판정한다. upstream 플러그인·훅·npm 패키지·MCP·외부 서비스는 설치하지 않았고 민감 데이터 전송이나 운영 신뢰 단계 승격도 추가하지 않았다.
