# CALDEA-M1 결정 기록

## D001 — 시딩 문서의 링크 검증 경계

- 상태: **승인**, 2026-09-26, 사용자 명시 지시.
- 배경: 수정 금지된 시딩 권위 문서의 상대 링크는 원본 Mnemosyne 저장소의 `docs/AI_MEMORY_COMPARISON.ko.md` 위치를 기준으로 작성되어 있다. 복제된 references 위치를 기준으로 검사하면 원본에 존재하는 파일도 깨진 링크가 된다.
- 결정: 시딩 4개 원문은 무수정 보존한다. **새 산출물의 상대 링크만 전부 검사**한다. 시딩 문서의 원본 저장소 상대 링크는 **원본 경로 기준 검증 대상**으로 DoD에 명시한다.
- 실행: `scripts/verify.py`가 새 문서의 파일·앵커 링크와 시딩 SHA-256을 검사한다. `--source-links`는 권위 문서를 원본 위치에 놓인 것으로 해석해 링크 대상의 존재를 별도로 검사한다. 외부 체크아웃이 없으면 해당 검증은 실패로 표시하고 통과로 바꾸지 않는다.
- 결과: 배포 패키지는 개발자 개인 절대 경로에 의존하지 않는다. 시딩 링크 자체를 현재 리포에서 클릭 가능하다고 주장하지 않는다. 새 문서에서는 패키지 내 자료로 연결한다.

## D002 — 문서 간 버전 차이의 처리

- 상태: **PROPOSAL 채택**, M1 구현 판단.
- 기억 역할·구현 한계는 시딩 권위 비교 문서를 따른다. 설치 문법·하네스 지원은 읽은 로컬 설치 문서와 CLI help를 기준으로 버전 차이를 함께 명시한다.
- Codex 0.145.0 이상 SessionEnd 지원이라는 현행 문서 설명과 과거 전략 문서의 “없음”을 구분한다. 브리프의 Codex/agy finalize-session 의무는 유지하되 정확한 세션 ID를 사용하고 이미 종료된 세션은 확인 기록으로 대체한다.
- 기존 pitfalls의 “mtime이 완료 보고보다 뒤여야 한다” 문장은 저장 경쟁을 검출하는 근거로 사용할 수 없다. 변경 요청 이후 저장됐는지, 완료 보고 이전에 저장이 끝났는지, 두 관측에서 안정적인지를 함께 확인한다. mtime 단독으로 변경 내용을 증명하지 않는다.

## D003 — agent-skills의 고효익 점검만 내장

- 상태: **승인**, 2026-10-08 11:16:44 NZDT, 사용자 요청 “칼데아를 보강하는 차원에서 이점이 클거만 선별하고 붙여보자”.
- 출처: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/tree/1401c8b8030e023baeebb31781a6653fe8e93026), upstream revision `1401c8b8030e023baeebb31781a6653fe8e93026`, MIT. [보안](https://github.com/addyosmani/agent-skills/blob/1401c8b8030e023baeebb31781a6653fe8e93026/skills/security-and-hardening/SKILL.md), [기준 보호](https://github.com/addyosmani/agent-skills/blob/1401c8b8030e023baeebb31781a6653fe8e93026/skills/constraint-driven-development/SKILL.md), [성능 측정](https://github.com/addyosmani/agent-skills/blob/1401c8b8030e023baeebb31781a6653fe8e93026/skills/performance-optimization/SKILL.md)의 원칙을 참고해 Caldea 문구로 재작성한다. upstream 원문·스크립트·공유 references를 복사·배포하지 않는다.
- 선택: 모든 변경의 검증 기준 약화 점검, 신뢰 경계 변경의 위협/오용 점검, 성능 요구·회귀 작업의 동일 조건 반복 측정과 변동폭 판정. 나머지 작업은 적용 이유/비적용 이유만 남겨 비용을 제한한다.
- 통합: 자기완결적인 기존 `milestone-loop`, 설치기의 AGENTS 라우팅, 프로젝트 템플릿, 운영 문서에 반영한다. 설치기는 기존 경로·백업·멱등 계약 그대로 스킬과 마커를 갱신하며 외부 패키지·자료 fetch가 필요하지 않다.
- 제외: 전체 25개 스킬 설치, meta-router, lifecycle 명령, task별 자동 커밋, 추가 doubt/review 루프, mutation 실험, 자동 도구 설치·훅·외부 전송. reviewer는 read-only이며 DAG·dispatch·round·권한·기존 DoD·동일 head PASS는 Caldea가 소유한다.
- 판단 근거: 기존 오케스트레이션은 중복 도입하지 않고 제품 수준 보안·검사 우회·가짜 성능 개선을 겨냥한다. 테스트 삭제/억제는 근거를 검토하며 단순 패턴 존재를 결함으로 단정하지 않는다. 수치 기본값이나 프로젝트 전체 성능 검사를 추가하지 않는다.
- 검증 경계: 패키지/설치 검사와 도구 없는 점검 시나리오 응답은 실제 Orca/CI 실행이나 결함 감소·시간/토큰 절감을 입증하지 않는다. 실측 순이득은 운영에서 추가 유효 finding·오탐·검증 비용으로 별도 판단한다.

## D004 — 버전 고정 배포와 하네스 설치 진입점

- 상태: **승인**, 2026-10-08, 사용자 요청 “새 버전 설치 방법을 에이전트 하네스가 인식할 수 있게하고, 커밋 푸시 후 버전 태그 지정”.
- 결정: 기존 태그/버전 파일이 없으므로 최초 버전은 `0.1.0`, 태그는 `v0.1.0`으로 지정한다. [VERSION](../VERSION)을 정본으로 하고 스킬 metadata, 설치기 버전 출력, 대상 AGENTS 마커에 버전을 연결한다.
- 하네스 진입점: 루트 AGENTS.md와 CLAUDE.md, 설치된 milestone-loop, 대상 Caldea 마커가 [버전 고정 설치·갱신 지침](install.md)으로 안내한다. 요청 태그 체크아웃의 버전·같은 대상/스킬 경로의 `--check`·실제 로드된 버전을 따로 확인한다.
- 안전 경계: 기존 수정 체크아웃·프로젝트 계약·외부 연동을 덮어쓰지 않는다. 구버전은 기존 백업/멱등 설치 계약으로 갱신한다. 혼합 VERSION/스킬은 쓰기 전에 거부한다. 홈 스킬 공유 영향을 안내하며 하네스 reload 성공을 패키지 복사만으로 주장하지 않는다.
- 배포 범위: 요청한 main 커밋·push 후 같은 revision에 annotated tag를 지정·push한다. GitHub Release 게시나 전역 설치 갱신은 이번 요청에 포함하지 않는다.
- 배포 후 수정: 비공개 저장소의 비인증 HTTPS clone이 `could not read Username`으로 실패했고 `gh repo view ... --json isPrivate,visibility`가 PRIVATE를 확인했다. 기존 SSH 인증의 태그 clone은 성공했다. 접근 전제를 보완한 `0.1.1`을 새 커밋·태그로 배포하며 공개한 `v0.1.0`은 유지한다.

## D005 — 작업 단위 맥락 체크포인트

- 상태: **승인**, 2026-10-09, 사용자 요청 “적당히 보강만 해주고 새 버전으로 업데이트”.
- 결정: `0.1.2` 패치로 기존 브리프/완료 보고에 `context_start`·`context_end`를 추가한다. 새 작업·인계·재개에서 최신 관련 근거와 실제 revision을 확인하고, 코디네이터가 종료 증거와 대조한 뒤 후속 의존 작업을 허용한다.
- 비용 경계: 같은 작업의 유효한 맥락은 재사용한다. 외부 관련 변경 때 영향 자료만 다시 읽으며 매 도구 호출의 전체 기억 조회, 별도 상태 파일 체계·훅·라우터·추가 리뷰 루프는 만들지 않는다.
- 안전 경계: 실패/BLOCKED도 종료 보고를 남긴다. reviewer는 판정 응답만 제출하고 코디네이터가 연결한다. 기존 DoD·동일 head PASS·최대 3라운드·scope·민감 데이터 규칙을 유지하며 작업 보고와 세션 handoff/finalize를 구분한다.
- 배포: main 커밋·push와 새 annotated tag 후 현재 하네스의 관리 스킬을 기존 설치기로 백업·갱신한다. 다른 프로젝트 AGENTS나 다른 하네스 설정·MCP·훅은 변경하지 않는다. 실제 설치/로드 확인과 자동 강제 실행은 별도 판정한다.

## D006 — 이해하기 쉬운 응답 표현 스킬 배포

- 상태: **승인**, 2026-10-13, 사용자 요청 “i-have-adhd를 Caldea Workflow에 통합하고 AGENTS.md 응답을 이해하기 쉽게” 및 버전 갱신·remote push.
- 출처: [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd/tree/1ecea1993b7fce257ffbd686c070948b5e07eda6), [upstream SKILL.md](https://github.com/ayghri/i-have-adhd/blob/1ecea1993b7fce257ffbd686c070948b5e07eda6/skills/i-have-adhd/SKILL.md), [MIT LICENSE](https://github.com/ayghri/i-have-adhd/blob/1ecea1993b7fce257ffbd686c070948b5e07eda6/LICENSE). Pinned revision `1ecea1993b7fce257ffbd686c070948b5e07eda6`; Copyright (c) 2026 Ayoub Ghriss. Caldea의 한국어 표현 규칙으로 적응하고 라이선스를 함께 배포한다. 사용자의 ADHD 진단이나 특성을 가정하지 않는다.
- 통합: `0.2.0`에서 기존 `milestone-loop`와 별도 `i-have-adhd` 스킬 및 MIT LICENSE를 한 설치기로 복사·검사한다. 기존 AGENTS의 관리 마커 밖 내용은 보존한다. 마일스톤 밖에도 읽기 쉬운 표현을 사용하지만 명시적인 사용자 언어·형식·길이 요청과 일반 모드 opt-out이 우선한다.
- 안전 경계: 기존 비관리 동명 upstream 스킬을 덮어쓰지 않고 승인된 격리 `--skills-dir`과 실제 하네스의 발견 우선순위를 확인한다. upstream 플러그인·훅·npm 패키지·네트워크 fetch·전역 설정은 자동 설치하지 않는다. DoD·권한·동일 head PASS·리뷰 라운드·필수 보고 스키마와 증거에는 변경이 없다.
- 배포 범위: 요청한 `0.2.0` main 커밋·push와 같은 revision의 annotated tag·push. GitHub Release 게시는 포함하지 않으며 다른 프로젝트 설치나 외부 연동 변경도 포함하지 않는다. 설치 복사·`--check`와 실제 하네스 reload·두 스킬의 로드 확인은 별도 증거로 판단한다.

## D007 — 명시적 Caldea 설치 갱신 스킬

- 상태: **승인**, 2026-10-13, 사용자 요청으로 Caldea Workflow 갱신 절차를 새 스킬로 배포하고 `0.3.0` 버전·remote push.
- 결정: `caldea-update`는 새 updater CLI/daemon이 아닌 에이전트 절차다. 설치기는 `milestone-loop`, `i-have-adhd`, `caldea-update` 세 스킬과 `i-have-adhd/LICENSE` 및 AGENTS 관리 마커만 복사·검사한다. remote fetch는 설치기에 넣지 않는다.
- 권한 경계: 대상 설치의 명시적 갱신 요청만 쓰기 권한이다. 버전·상태 조회는 읽기 전용이며 이 소스 패키지의 구현·릴리스 요청은 다른 프로젝트/홈 설치 갱신을 승인하지 않는다. 자동 갱신·자동 다운그레이드·파괴적 롤백은 하지 않는다. 기본 홈 스킬의 공유 영향과 기존 비표준 `--skills-dir`을 확인한다.
- 버전 선택: 지정 태그가 우선한다. 없으면 승인된 remote의 `git ls-remote --tags --refs` 결과 중 `vMAJOR.MINOR.PATCH` 안정 태그만 세 숫자 semver 비교로 최고 버전을 고른다. 설치된 메타데이터·GitHub Releases 부재·사전순·날짜로 최신을 추측하지 않는다. 선택 태그를 새 경로에 clone하고 새 checkout의 `docs/install.md`·`CHANGELOG.md`를 읽으며 태그/VERSION 일치를 확인한다. 기존 SSH 또는 승인된 HTTPS 인증을 재사용하고 토큰·키 열람, 공개 전환, 보안 설정 변경은 금지한다.
- 안전·완료: 실제 대상·하네스·로드된 스킬 루트를 확인하고 동일 인자의 설치기 `--check`를 쓰기 전후 수행한다. exit 1은 드리프트 확인일 뿐 수리가 아니며 exit 2 충돌/입력 오류는 override하지 않는다. 동일 상태는 강제 쓰지 않는다. 프로젝트 AGENTS 마커 밖 규칙·DoD와 외부 설정을 보존하고 symlink/비관리 동명 스킬을 덮어쓰지 않는다. 새 세션의 하네스 restart/reload 후 세 스킬의 실제 로드 경로·metadata와 프로젝트 마커를 확인한다. 파일 일치는 native load 증거가 아니며 교체된 갱신 스킬 지침을 다시 읽는다.
- 배포 범위: 요청한 `0.3.0` 소스 릴리스만 main 커밋·push 및 같은 revision의 annotated `v0.3.0` 태그·push로 배포한다. 다른 프로젝트나 홈의 설치, 새 플러그인·MCP·전역 훅 설정은 포함하지 않는다.
