---
name: caldea-update
description: "칼데아 워크플로우 설치본을 최신 안정 릴리스 또는 사용자가 지정한 태그로 안전하게 갱신한다. 기존 프로젝트·하네스·스킬 경로를 확인하고 버전 고정 checkout, 설치·읽기 전용 검사, 실제 로드 증거를 구분한다. 칼데아 업데이트·갱신·버전 확인 요청에 사용하며 구현·릴리스 요청만으로 설치본을 변경하지 않는다."
metadata: {"version": "0.3.0"}
---
<!-- caldea-workflow:managed-skill:v1 -->

# Caldea Workflow 업데이트

명시적으로 승인된 프로젝트의 Caldea 설치본만 갱신하는 에이전트 실행 절차다. 스킬 자체가 실행 데몬·자동 업데이트 훅·새 CLI는 아니다. 패키지의 기준 안내는 [이 버전의 설치 지침](https://github.com/tipsy-kereru/caldea-workflow/blob/v0.3.0/docs/install.md)이지만, 업데이트 대상 버전의 checkout에서 읽은 설치 지침을 우선한다. 설치된 이 스킬의 `metadata.version`이나 고정 링크가 최신 배포 버전을 뜻하지 않는다.

## 요청과 권한

- “칼데아 업데이트해줘”, “이 프로젝트를 vX.Y.Z로 갱신해줘”는 해당 설치본 갱신 요청이다. “버전 확인”, “새 버전이 있나”는 조회만 수행하고 설치하지 않는다. 패키지 소스의 개발·버전업·커밋·push 요청은 대상 설치본·사용자 홈 갱신 승인이 아니다.
- 기존 AGENTS·실제 로드된 스킬 경로·사용 하네스를 먼저 확인한다. 같은 작업의 유효한 증거는 재사용한다. 대상 프로젝트, `agents|claude`, 실제 스킬 루트, 현재 버전, 요청 버전, 공유 영향과 권한을 기존 작업 보고의 `context_start`에 남긴다. 도구·리포 증거로 확인 가능한 값은 사용자에게 다시 묻지 않는다.
- `--skills-dir`을 사용한 설치는 그 실제 경로를 유지한다. 기본 홈은 여러 프로젝트가 공유하므로 다른 프로젝트의 관리 마커가 자동 갱신되지 않는다는 영향을 알리고 요청 범위를 넘는 갱신은 하지 않는다. 경로가 여러 개여서 대상을 확정할 수 없을 때만 구체적인 선택을 묻는다.
- 새로운 MCP·훅·플러그인·서버·전역 인증 설정·자동 병합·저장소 공개·provider 전송은 승인에 포함되지 않는다. 조회/clone에는 기존 승인된 GitHub 인증만 재사용하며 토큰·개인 키를 열람하거나 출력하지 않는다.

## 1. 대상 릴리스 확정

사용자가 정확한 안정 태그를 지정했다면 그 태그를 사용한다. 버전을 지정하지 않았다면 다음 읽기 전용 명령으로 공식 원격 태그를 조회한다.

```bash
git ls-remote --tags --refs git@github.com:tipsy-kereru/caldea-workflow.git
```

응답의 `refs/tags/vMAJOR.MINOR.PATCH` 중 각 숫자에 불필요한 선행 0이 없는 안정 태그만 선택한다. 세 숫자를 정수로 비교해 가장 큰 SemVer를 선택한다. `v0.10.0`은 `v0.9.9`보다 새 버전이며 사전식 정렬·태그 날짜·출력 순서로 판단하지 않는다. `-rc`, `-beta` 같은 사전 릴리스와 `+build` 태그는 이 기본 안정 버전 후보에서 제외한다. `--refs`로 annotated tag의 `^{}` 행을 제외한다. GitHub Release가 없어도 원격 태그를 기준으로 진행하며 `main`을 최신 릴리스로 대신 사용하지 않는다.

네트워크/권한 오류나 안정 태그 부재는 확인 불가로 보고한다. 로컬 캐시·설치된 구버전 링크를 “최신”으로 사용하지 않는다. HTTPS 인증 환경에서는 이미 승인된 HTTPS URL로 동일 조회를 수행할 수 있다. SSH host key 검사를 우회하지 않는다.

현재 버전보다 낮은 태그는 자동 적용하지 않는다. 명시적인 다운그레이드 승인과 대상 버전의 호환/복구 지침 없이는 조회 결과와 필요한 결정만 보고한다. 조회 요청이면 현재 버전·원격 후보·차이를 보고하고 여기서 끝낸다.

## 2. 고정 checkout과 대상 지침 읽기

선택한 실제 태그와 아직 없는 checkout 경로를 정하고 아래 자리표시자를 치환한다. 명령은 읽은 CLI 계약에 맞게 실행한다.

```bash
git clone --branch <selected-tag> --single-branch git@github.com:tipsy-kereru/caldea-workflow.git <unused-checkout>
# 이후 명령의 cwd는 <unused-checkout>
git describe --tags --exact-match
bash install.sh --version
```

선택한 태그가 가리키는 revision과 실제 HEAD가 일치하는지 확인한다. 동일 revision에 태그가 여러 개면 `git describe`가 다른 태그를 표시할 수 있으므로 선택한 태그의 peeled commit과 HEAD를 대조한다. VERSION의 `X.Y.Z`, 선택한 `vX.Y.Z`, `install.sh --version` 출력을 대조한다. 버전 또는 revision이 불일치하면 쓰기를 시작하지 않는다. checkout의 **`docs/install.md` §0, CHANGELOG.md, VERSION**을 읽고 변경 범위·설치 계약·필수 환경을 확인한다. 새 설치기의 필수 스킬 목록과 각 metadata도 대상 checkout 기준으로 확인한다.

기존 수정 checkout에 checkout/reset/pull하지 않는다. 설치기를 대상 프로젝트 cwd에서 잘못 찾지 말고 고정 checkout의 설치기를 사용한다. read 도구가 비공개 GitHub 문서를 읽지 못하면 인증된 로컬 checkout을 읽는다. 새 버전의 지침에 추가 권한·구성이 필요하면 기존 승인으로 확대하지 않고 필요한 결정만 요청한다.

## 3. 같은 대상에서 검사와 갱신

확인한 절대 프로젝트 경로, target, 실제 스킬 루트를 두 명령에서 동일하게 사용한다. cwd는 고정 checkout이다.

```bash
bash install.sh --project <project> --target <agents-or-claude> --skills-dir <actual-skills-root> --check
# 갱신 요청이 승인됐고 검사 입력이 유효한 경우:
bash install.sh --project <project> --target <agents-or-claude> --skills-dir <actual-skills-root>
bash install.sh --project <project> --target <agents-or-claude> --skills-dir <actual-skills-root> --check
```

첫 검사 종료 코드의 의미:

| exit | 처리 |
|---|---|
| 0 | 선택한 릴리스의 파일·관리 마커 일치. 불필요한 재설치 없이 로드 확인으로 진행 |
| 1 | 누락/드리프트. 조회만으로는 수정되지 않는다. 승인된 갱신 요청이면 설치 후 재검사 |
| 2 | 잘못된 인자·마커·경로·비관리 스킬 충돌 등. 원본을 보존하고 원인을 해결하기 전 설치하지 않음 |

설치기는 `milestone-loop`, `i-have-adhd`, `caldea-update`와 동봉 LICENSE 및 AGENTS의 Caldea 관리 블록만 관리한다. 프로젝트 권한·DoD·다른 관리 마커·사용자 파일과 기존 외부 연동은 보존한다. 비관리 동명 스킬이나 symlink 충돌은 `--force`·삭제·소유 마커 삽입으로 우회하지 않는다. 필요한 경우 사용자 승인과 실제 하네스 발견 경로를 확인한 별도 스킬 루트로 설치한다. 기존 경로를 바꾸는 결정은 암묵적으로 하지 않는다.

출력의 실제 backup 경로와 명령별 cwd/exit를 기록한다. 검사 실패를 성공으로 바꾸지 않는다. 부분 실패에는 설치기의 복구 결과를 확인하고 남은 차이를 보고한다. 백업에서의 수동 복원도 승인된 해당 변경에 한정하며 일괄 삭제·reset·자동 다운그레이드를 실행하지 않는다.

## 4. 실제 로드와 완료 판정

이 스킬도 자기 업데이트 대상이다. 파일 교체 후 새 `caldea-update` 본문을 다시 읽고 새 버전의 완료 지침을 확인한다. 디스크 교체만으로 현재 세션의 스킬 목록·기억이 reload됐다고 하지 않는다.

선택한 하네스가 실제 지원하는 restart/reload 절차를 수행하고 **같은 프로젝트의 새 세션**에서 확인한다. 스킬 URI나 하네스 발견 목록을 통해 실제 선택된 경로를 확인하며 원하는 절대 파일을 직접 읽은 것만으로 자동 발견을 주장하지 않는다.

- 대상 버전이 제공하는 모든 스킬(현재 패키지에서는 세 스킬)의 실제 경로·로드한 `metadata.version`.
- 프로젝트 AGENTS의 Caldea 버전과 같은 target/skills-dir의 `--check` exit 0.
- 필요한 LICENSE 설치, 실제 백업 경로, 보존한 외부 연동, 미실행/차단 항목.

새 세션 로드를 실행할 수 없으면 **“파일 갱신·검사 완료, 실제 하네스 로드 미확인”**으로 구분하고 설치 전체 완료를 주장하지 않는다. 다른 경로의 구버전이 발견되면 중복 설치를 무조건 삭제하지 않고 우선순위·사용자 설정을 확인한다. 요청 범위 밖 하네스를 재시작하거나 다른 프로젝트의 AGENTS를 변경하지 않는다.

기존 완료 보고의 `context_end`에는 `요청 tag / 원격·checkout revision / package --version / project / harness / actual skills-root / 스킬별 loaded path·metadata.version / AGENTS 버전 / 검사 cwd·exit / backup / 외부 설정 보존 / 차단·다음 행동`을 실제 증거로 기록한다. 최신 없음·이미 동일·실패도 결과를 남긴다. 업데이트 보고와 세션 handoff/finalize는 구분한다. 응답 표현은 사용자 언어·형식과 `i-have-adhd`의 적용 상태를 따르며 미해결일 때만 다음 행동 하나로 끝낸다.
