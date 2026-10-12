# Caldea Workflow · 칼데아 워크플로우

사용자 지시를 **마일스톤 개발 → 검증 → PR 리뷰 → 개선 → 다음 마일스톤**으로 연결하는 에이전트용 워크플로우 패키지입니다. Orca가 작업을 조율하고 OMP·Codex·Antigravity·Claude Code 같은 하네스가 실행하는 운영 절차를 제공합니다.

현재 M1 패키지에는 설치 가능한 `milestone-loop`(실행 절차)와 `i-have-adhd`(응답 표현) 스킬, 프로젝트 지침 템플릿, 설치기와 운영 문서가 포함됩니다. **독립 실행 애플리케이션, 실행 데몬, Slack 봇은 아닙니다.** 아래 루프는 설치한 하네스가 수행할 운영 계약이며, 패키지 설치만으로 CI·외부 서비스·자동 병합이 활성화되지는 않습니다.

현재 릴리스: **v0.2.0** ([VERSION](VERSION), [변경 이력](CHANGELOG.md)). 하네스에게 설치·갱신을 맡기려면 [설치 지침](docs/install.md)을 읽히세요. 루트 `AGENTS.md`와 `CLAUDE.md`, 설치된 스킬과 프로젝트 관리 마커에도 버전·설치 경로가 안내됩니다.

저장소는 비공개입니다. 읽기 권한과 기존 GitHub SSH 인증이 필요합니다. 인증된 HTTPS를 사용하는 환경의 대체 절차도 설치 지침에 있습니다.

```text
사용자 지시 → 마일스톤 선정 → 개발 → 기계 검증 → 커밋 → PR
                          ↑                          ↓
                          └── 개선 ← 리뷰(최대 3라운드)
                                      ↓ PASS
                                 다음 마일스톤
```

## 제공하는 것

- **마일스톤 실행 절차:** 범위·완료 조건(DoD)·권한을 확인하고, 검증과 리뷰 증거를 남기는 `milestone-loop` 스킬.
- **읽기 쉬운 응답:** [i-have-adhd](skills/i-have-adhd/SKILL.md)를 읽고 마일스톤 밖의 대화에도 결과·행동 우선, 짧은 단계, 분명한 오류 설명을 적용합니다. ADHD 진단을 전제하지 않으며 사용자 언어·형식 요청과 필수 증거가 우선합니다. [원 저작자 MIT 라이선스](skills/i-have-adhd/LICENSE)를 동봉합니다.
- **작업 맥락 체크포인트:** 새 작업·인계·재개 때 최신 근거를 확인하고 종료 보고를 남깁니다. 같은 작업의 유효한 맥락은 재사용하며, 코디네이터가 증거를 대조한 뒤 후속 의존 작업을 허용합니다.
- **프로젝트 지침:** 기존 `AGENTS.md`에 병합할 게이트·보고·실패 복구 규칙.
- **멱등 설치기:** 스킬 복사, AGENTS 관리 블록 갱신, 변경 전 백업, 읽기 전용 설치 상태 검사.
- **운영 가이드:** 하네스별 MCP·훅 연결, 기억 도구 역할 분리, 승인된 Slack 채널 보고와 단계별 자동화 승격 조건.

## 빠른 시작

**필수 환경:** Git(저장소 복제 및 커밋·PR 루프), Bash 3.2 이상, Python 3.9 이상. 설치 대상 프로젝트 디렉터리는 미리 존재해야 합니다.

```bash
git clone --branch v0.2.0 --single-branch git@github.com:tipsy-kereru/caldea-workflow.git caldea-workflow-v0.2.0
cd caldea-workflow-v0.2.0
bash install.sh --version

# /absolute/path/to/project를 실제 대상 프로젝트 경로로 바꾸세요.
bash install.sh --project /absolute/path/to/project --target agents
bash install.sh --project /absolute/path/to/project --target agents --check
```

기본 설치 결과:

- 한 번의 설치로 `~/.agents/skills/milestone-loop/SKILL.md`와 `~/.agents/skills/i-have-adhd/SKILL.md` 및 후자의 `LICENSE`를 복사합니다. 외부 fetch·플러그인·훅은 이 패키지 설치에 필요하지 않습니다.
- 대상 프로젝트의 `AGENTS.md`에 `caldea-workflow:start` / `caldea-workflow:end` 마커 블록을 삽입하거나 갱신합니다. 블록 밖의 기존 내용은 보존합니다.
- 변경하는 기존 파일은 `.bak-<타임스탬프>-<고유값>`으로 백업합니다. 같은 내용으로 재설치하면 파일과 수정 시각을 바꾸지 않습니다.

Claude Code용 스킬 경로를 사용하려면:

```bash
bash install.sh --project /absolute/path/to/project --target claude
bash install.sh --project /absolute/path/to/project --target claude --check
```

`--target claude`는 `~/.claude/skills/`에 설치합니다. `CLAUDE.md`는 자동 변경하지 않으므로, 기존 지침을 보존하면서 첫 줄의 `@AGENTS.md` import를 직접 확인해야 합니다.

### 설치 옵션

| 옵션 | 동작 |
|---|---|
| `--project PATH` | 기존 대상 프로젝트 경로. 생략하면 현재 작업 디렉터리 |
| `--target agents\|claude` | 스킬 설치 위치 선택. 기본값은 `agents` |
| `--skills-dir PATH` | 스킬 루트를 직접 지정. `--target`보다 우선 |
| `--check` | 파일을 변경하지 않고 설치 내용 일치 여부 검사 |
| `--version` | 체크아웃한 패키지 버전 출력, 설치하지 않음 |

`--check`의 종료 코드는 일치 `0`, 누락·드리프트 `1`, 잘못된 인자·마커·경로 충돌 등 오류 `2`입니다. 설치기는 symlink 대상이나 Caldea 소유가 아닌 동명 스킬을 자동 덮어쓰지 않습니다. 기존 upstream `i-have-adhd`와 충돌하면 보존하고 해당 하네스가 읽는 승인된 격리 스킬 루트를 `--skills-dir`로 지정하세요. 실제 스킬 발견 우선순위를 확인해 동명 스킬이 중복 로드되지 않게 하며 upstream 플러그인을 자동 설치하지 않습니다.

기존 설치는 새 태그 체크아웃에서 동일 대상·스킬 경로로 설치와 `--check`를 실행해 갱신합니다. 하네스를 재시작/reload한 뒤 대상 프로젝트의 AGENTS 버전과 실제 로드된 **두 스킬 각각**의 경로·`metadata.version` (`0.2.0`)을 확인하세요. 기본 홈 스킬은 여러 프로젝트가 공유할 수 있습니다. 상세 절차와 응답 예시·일반 모드 전환은 [설치 지침](docs/install.md)을 따릅니다.

## 설치 후 사용

1. [설치 지침](docs/install.md)에 따라 사용할 하네스와 MCP·훅 부착 대상을 확정하고, ai-memory·Mnemosyne·Orca를 연결합니다. 설치기는 외부 서버나 사용자 설정을 대신 구성하지 않습니다.
2. [AGENTS 템플릿](templates/AGENTS.md)을 참고해 대상 프로젝트의 범위, 필수 검증 명령, DoD와 작업 권한을 기존 지침에 반영합니다.
3. 하네스에 다음처럼 요청합니다.

   ```text
   milestone-loop 스킬로 승인된 마일스톤을 수행하라.
   프로젝트 AGENTS.md의 범위·DoD·권한을 따르고,
   필수 검증 명령의 종료 코드와 증거 경로를 보고하라.
   ```

4. [운영 매뉴얼](docs/workflow.md)에 따라 리뷰·개선·재검증을 수행합니다. 최종 PASS와 같은 revision의 필수 검증 증거를 확보한 뒤 다음 마일스톤으로 진행합니다.

마일스톤 작업이 아니어도 설치된 `i-have-adhd`를 읽고 답변에 적용합니다. 사용자가 “일반 모드로 답해줘” 또는 “ADHD 모드 중지”라고 하면 표현 방식 적용을 멈추고, 다시 요청할 때 재개합니다. 필수 검사·권한·보고 형식은 바뀌지 않습니다.

### 운영 원칙과 경계

- **기계 검증과 자연어 지침을 구분합니다.** 타입 검사·테스트·빌드 같은 게이트는 실제 CI 필수 체크로 연결해야 강제됩니다. AGENTS나 스킬만으로는 강제되지 않습니다.
- **자동 병합은 기본 권한이 아닙니다.** [로드맵](docs/ROADMAP.md)의 별도 승격 조건과 명시적으로 승인된 권한을 따릅니다.
- **기억 도구의 역할을 분리합니다.** ai-memory는 세션 연속성·이전 결정·인계, Mnemosyne는 구조화 지식·코드 관계를 담당합니다. 같은 질문을 양쪽에 중복 전송하지 않습니다. 상세 경계는 [권위 비교 문서](references/authority-memory-comparison.ko.md)를 따릅니다.
- **Slack 연동은 별도 구성입니다.** 승인된 채널에만 보고하며, 그룹에서 특정 에이전트가 멘션된 요청은 해당 에이전트만 수행합니다. 제한된 Slack/Onyx 원문과 시크릿을 일반 graph나 세션 기억에 자동 합류시키지 않습니다.
- **고효익 점검만 보강합니다.** [선별 품질 보강](skills/milestone-loop/SKILL.md#선별-품질-보강)은 모든 변경의 검증 기준 약화, 신뢰 경계 변경의 보안 위협, 성능 요구·회귀의 동일 조건 측정을 다룹니다. 별도 agent-skills 설치·라우터·훅 없이 기존 역할·권한·DoD 안에서 적용합니다. 자연어 점검만으로 CI 강제나 품질 개선이 입증되는 것은 아닙니다.

## 문서 안내

| 문서 | 내용 |
|---|---|
| [한국어 개요](README.ko.md) | 신뢰 곡선, Feature Map, 기억 도구 등 핵심 개념 |
| [설치 지침](docs/install.md) | 환경 확인, 하네스별 서버·MCP·훅 연결 |
| [운영 매뉴얼](docs/workflow.md) | 상태 전이, 리뷰, 실패 복구, 보고 계약 |
| [AGENTS 템플릿](templates/AGENTS.md) | 프로젝트별 범위·DoD·검증 게이트 작성 |
| [milestone-loop 스킬](skills/milestone-loop/SKILL.md) | 설치해서 사용하는 실행 절차 |
| [로드맵](docs/ROADMAP.md) | 단계별 진입·종료 조건과 자동화 승격 |
| [연구 종합](docs/00-research.md) | 설계 근거와 VERIFIED/PROPOSAL 구분 |
| [결정 기록](docs/DECISIONS.md) | 승인된 설계·검증 경계 |
| [M1 검증 기록](docs/VERIFICATION.md) | 기존 검증 증거와 외부 연동 검증의 한계 |

## 패키지 검증

저장소 루트에서 실행합니다. Python 검증 스크립트는 표준 라이브러리만 사용합니다.

```bash
bash -n install.sh
python3 scripts/verify.py
python3 scripts/test_install.py
git diff --check
```

`verify.py`는 필수 산출물, 문서 상대 링크·앵커, 스킬 frontmatter, Bash 구문, diff 공백과 시딩 원문의 해시를 검사합니다. `test_install.py`는 임시 프로젝트와 별도 스킬 경로에서 설치·재설치·백업·드리프트·충돌 처리를 검증합니다.

시딩 문서의 원본 저장소 링크까지 검사하려면 원본 체크아웃이 있는 환경에서 `python3 scripts/verify.py --source-links`를 실행합니다. **패키지 검사 통과는 실제 MCP 왕복, 하네스 인계, GitHub PR 리뷰·병합, Slack 발송의 성공 증거가 아닙니다.** 외부 연동은 대상 환경에서 별도로 검증해야 합니다.
