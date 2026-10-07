# 칼데아 워크플로우

사용자 지시를 마일스톤 개발, 기계 검증, 커밋, PR 리뷰, 개선과 다음 마일스톤으로 연결하는 **에이전트용 배포 패키지**다. Orca가 작업을 조율하고 OMP·Codex·Antigravity·Claude Code가 실행한다.

M1은 문서, 설치 가능한 `milestone-loop` 스킬, AGENTS 템플릿, 멱등 설치기를 제공한다. 실행 데몬이나 Slack 봇을 제공하지 않는다. 아래 전체 루프는 **PROPOSAL: 설치한 하네스가 수행할 운영 계약**이다. 패키지 검사 결과와 실제 외부 서비스 실행 결과는 구분한다.

현재 배포는 **v0.1.1**이며 [VERSION](VERSION)과 [변경 이력](CHANGELOG.md)으로 식별한다. 설치·갱신을 맡길 하네스에는 [설치 지침](docs/install.md)의 버전 고정 절차부터 읽힌다. 비공개 저장소의 읽기 권한과 승인된 GitHub SSH 또는 HTTPS 인증이 필요하다. 루트 AGENTS/CLAUDE와 설치된 스킬·프로젝트 마커가 이 절차를 안내한다.

```text
지시 → 마일스톤 선정 → 개발 → 검증게이트 → 커밋 → PR
     → 리뷰(최대 3라운드) → 개선 → 재검증 → PASS → 다음 마일스톤
                         단계 완료·주기 하트비트 → 승인된 Slack 채널
```

## 핵심 개념

- **신뢰 곡선:** 처음에는 사람이 리뷰한다. 게이트의 실패 탐지 증거가 쌓일 때만 리뷰 자동화, 제한된 자동 병합, 스킬 Eval로 확장한다.
- **강한 제약:** 타입 검사, 테스트, 빌드, 의존성 규칙처럼 실패 시 다음 상태로 넘어가지 못하게 하는 검사다. 실제 CI 필수 체크로 연결해야 강제된다.
- **약한 제약:** AGENTS.md, 스킬, 자연어 리뷰는 행동을 안내한다. 이 패키지를 설치했다는 사실만으로 CI 게이트가 생기지는 않는다.
- **Feature Map:** 기능 진입 경로·관련 코드·재현 명령·기대 결과를 연결한다. Mnemosyne graph/wiki가 코드 위치 탐색을 돕고 실제 동작은 소스와 런타임으로 검증한다.
- **헤드 셰프:** 사용자가 범위와 승격 권한을 정하고 코디네이터가 의존성·증거·다음 작업을 관리한다. 반복 리뷰 지적은 PStack 방식으로 스킬과 기계 검사에 반영한다.

## 기억 도구의 경계

[권위 비교 문서](references/authority-memory-comparison.ko.md)를 따른다. ai-memory는 page·observation·session·handoff를 통해 **작업 연속성**을 담당한다. Mnemosyne는 entity·relation·scope·entity history로 **구조화 지식과 코드 관계**를 담당한다. 같은 질문을 두 도구에 중복 전송하지 않는다. 둘 중 하나를 다른 저장소로 대체하지 않는다.

`mnemosyne add`는 LLM 추출 경로이며 API 키가 없어도 CLI fallback이 가능하다. `ingest extract`의 coding Tree-sitter 경로와 다르다. ai-memory wiki만 백업해서 sessions·handoffs까지 복구할 수는 없다. Slack/Onyx 제한 원문은 일반 graph나 세션 기억에 자동 합류시키지 않는다.

## 빠른 시작

Bash 3.2 이상, Python 3.9 이상이 필요하다. `v0.1.1` 태그의 새 체크아웃에서 실행하며 기존 설치도 같은 대상·스킬 경로로 재설치한다. 기존 수정본을 덮어쓰지 않는 clone·갱신 절차는 [설치 지침](docs/install.md)을 따른다.

```bash
bash install.sh --version
# 대상 프로젝트가 이미 있어야 한다. 기본 스킬 위치: ~/.agents/skills/
bash install.sh --project /absolute/path/to/project --target agents
bash install.sh --project /absolute/path/to/project --target agents --check

# Claude Code용 스킬 위치: ~/.claude/skills/
bash install.sh --project /absolute/path/to/project --target claude
```

1. [설치 지침](docs/install.md)을 하네스에 전달하여 ai-memory·Mnemosyne·Orca를 연결한다. 패키지 설치기는 이 외부 설정을 대신 바꾸지 않는다.
2. [AGENTS 작성 가이드](templates/AGENTS.md)의 프로젝트·DoD·권한 필드를 기존 AGENTS에 병합한다. Claude Code는 기존 CLAUDE.md를 보존하면서 첫 줄의 `@AGENTS.md` import를 확인한다.
3. 하네스에 “milestone-loop 스킬로 지정 마일스톤을 수행하라”라고 지시한다. 각 필수 명령의 종료 코드와 증거 경로를 남긴다.
4. [운영 매뉴얼](docs/workflow.md)에 따라 PASS 후 다음 마일스톤으로 진행한다. 자동 병합은 [로드맵](docs/ROADMAP.md)의 별도 승격 조건을 따른다.

갱신 뒤 하네스를 재시작/reload하고 실제 로드한 스킬의 `metadata.version`과 프로젝트 AGENTS 버전을 확인한다. `--check`는 드리프트를 읽기 전용으로 표시할 뿐 갱신하지 않으며, 기본 홈 스킬 갱신은 다른 프로젝트에도 영향을 줄 수 있다.

## 구성과 검증

| 파일 | 용도 |
|---|---|
| [연구 종합](docs/00-research.md) | 설계 근거, VERIFIED/PROPOSAL 구분 |
| [로드맵](docs/ROADMAP.md) | 4단계 진입·종료 판정 |
| [설치 지침](docs/install.md) | 하네스별 서버·MCP·훅 연결 |
| [운영 매뉴얼](docs/workflow.md) | 상태 전이·실패 복구·보고 계약 |
| [AGENTS 템플릿](templates/AGENTS.md) | 프로젝트별 강제 게이트 정의 |
| [스킬](skills/milestone-loop/SKILL.md) | 단독 설치 가능한 실행 절차 |
| [설치기](install.sh) | 스킬 복사·마커 병합·백업·검사 |
| [결정 기록](docs/DECISIONS.md) | 승인된 링크 검사 경계 |

패키지 검증은 `bash -n install.sh`, `python3 scripts/verify.py`, `python3 scripts/test_install.py`, `git diff --check`로 실행한다. 새 산출물 상대 링크는 전부 검사한다. 시딩 원문은 수정하지 않으며 원본 저장소 상대 링크는 **원본 경로 기준 검증 대상**이다.
