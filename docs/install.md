# 하네스에게 내리는 설치 지침

이 문서를 받은 에이전트는 아래 순서대로 대상 프로젝트를 설정하라. 명령은 **VERIFIED(지정 로컬 문서·CLI help 확인)**이며, 대상 컴퓨터에서 실행하기 전에는 설치 완료로 표시하지 않는다. 명령의 경로·scope 값은 실행 환경에서 확정한다. API 키·토큰 값은 저장소·보고서·명령 기록에 쓰지 않는다.

## 1. 사전 확인과 패키지 설치

프로젝트 절대 경로, 기존 AGENTS/CLAUDE 규칙, 사용할 하네스, 정확한 ai-memory workspace/project 이름을 확인한다. 대상이 git 저장소가 아니어도 패키지 설치·메모리 와이어링은 가능하다(degaza-v2가 git-less인 실례). 단, 커밋→PR 리뷰 루프는 git이 필요하므로 `git init` 여부를 사용자 결정 사항으로 기록하고 임의로 초기화하지 않는다.

**MCP·훅 부착 대상은 사용자에게 확인하고 기록한다(필수 입력).** "설치한다"는 것이 곧 "모든 하네스에 붙인다"가 아니다. 부착 대상 후보는 codex CLI·codex desktop GUI·OMP·agy·Claude Code·코디네이터 에이전트(예: Hermes) 등이고, 각각은 MCP 등록과 lifecycle 훅이 별개 항목이다(§3 표). 누락된 대상은 사용자 지정 질문 도구로 묻고(Spokenly 환경이면 `ask_user_dictation`), 승인된 목록만 §3에 적용한다. 이미 동일 서버에 붙어 있는 하네스는 재등록하지 않고 재사용함을 보고에 기록한다. 코디네이터 에이전트는 구현 세션이 아니므로 훅이 기본 아니며, 부착은 명시 요청 시에만 한다.

### 설치 질문 스크립트 — 다지선다 (사용자 환경 확인)

아래 질문을 사용자 지정 질문 도구로 한 번에 제시한다. 각 질문은 **권장 기본값**이 있고, 미응답이면 기본값으로 진행하되 보고에 "기본값 적용"으로 기록한다. 사용자의 실제 환경에서 성립하지 않는 기본값(예: 기존 서버 부재)이면 실패 이유를 남기고 에스컬레이션한다.

| # | 질문 | 선택지 | 권장 기본값 |
|---|---|---|---|
| 1 | ai-memory MCP+훅을 붙일 하네스 (복수 선택) | ① codex CLI ② codex desktop GUI ③ OMP ④ agy ⑤ Claude Code ⑥ 코디네이터(Hermes) ⑦ 없음(서버만) | ① + ③ (구현 하네스만, 코디네이터는 요청 시) |
| 2 | ai-memory 서버 운영 방식 | ① macOS launchd 상주(로그인 시 자동 시작) ② 전용 터미널 수동 `serve` ③ 기존 서버·원격 서버 재사용 | ① (이미 49374 서버가 살아 있으면 ③) |
| 3 | ai-memory LLM 요약·consolidation | ① zero-LLM으로 시작(캡처·검색·인계 전부 작동) ② `openai-oauth`(ChatGPT 플랜) ③ `anthropic-oauth`(Claude 플랜) ④ API 키 사용 | ① (나중에 추가 가능) |
| 4 | ai-memory workspace/project 이름 | ① 폴더 basename 기본값 승인 ② 직접 지정 | ① (mono-repo·worktree면 marker 문서 기준 직접 지정) |
| 5 | 캡처 마커 범위 | ① 옵트인 + 시크릿 경로 ignore 기본(`**/*.env*`, `**/secrets/**`) ② 옵트인 + 사용자 지정 ignore ③ 마커 없음(이 프로젝트 기억 안 씀) | ① |
| 6 | git 저장소 여부 | ① 이미 git 저장소 ② `git init` 허용 ③ git 없이 진행 | ① (③은 커밋→PR 게이트가 동작하지 않음을 명시하고 승인 필요) |
| 7 | Mnemosyne 설치 (구조 지식 그래프) | ① 설치 + `coding` 도메인 시딩 + codex 훅 ② 설치만, 시딩 보류 ③ 미설치 | ① (팀 프로젝트의 자체 도구이며 ai-memory와 역할 분리) |
| 8 | Orca 프로젝트 등록 | ① 등록(github: identity, kind=git) ② 등록 안 함 | ① (git-less 프로젝트는 identity 불일치로 실패할 수 있음 — ⑥과 연동) |

답변 결과는 설치 보고서에 "질문/선택/기본값 여부" 열로 남긴다. 질문은 환경 확인(`command -v`) 결과로 이미 확정된 항목은 생략한다 — 예를 들어 `ai-memory`가 이미 설치돼 있으면 ②번 질문은 ③ 재사용으로 확정한다.

`command -v`와 각 `--version`으로 기존 실행 파일을 식별하고, 이미 설치된 서비스·사용자 설정을 재사용한다. 기존 설정을 백업하고 변경 전후는 credential 값을 제외해 비교한다. 로컬 참고 체크아웃은 읽기만 한다.

```bash
command -v python3 bash git orca ai-memory mnemosyne
python3 --version
# Caldea 패키지 루트에서 실행
bash install.sh --project /absolute/project --target agents
bash install.sh --project /absolute/project --target agents --check
```

설치기는 Bash 3.2+, Python 3.9+를 사용한다. `--target claude`는 `~/.claude/skills/milestone-loop`, 기본 `agents`는 `~/.agents/skills/milestone-loop`에 스킬을 복사한다. `--skills-dir /absolute/skills`로 테스트·비표준 하네스 경로를 지정할 수 있다. 명시한 skills-dir이 target보다 우선한다. AGENTS에는 Caldea 시작/종료 마커 사이만 삽입·갱신하고 기존 바이트를 보존한다. 변경되는 기존 파일은 `.bak-UTC타임스탬프-고유값`으로 백업한다. 동일 내용 재설치는 파일과 mtime을 바꾸지 않는다.

`--check`는 설치할 내용을 기준으로 스킬·AGENTS 마커의 일치를 읽기 전용으로 검사한다. 일치하면 exit 0, 누락/드리프트는 1, 잘못된 인자·중복/불완전 마커·충돌 경로는 2다. 기존 symlink 목적지나 다른 사용자의 동명 스킬을 자동 덮어쓰지 않고 오류로 보고한다. 변경 전 백업으로 수동 복원할 수 있다. 설치기는 서버·MCP·훅·Orca 등록을 수행하지 않는다.

[AGENTS 템플릿](../templates/AGENTS.md)을 보고 필수 명령·보고 경로를 기존 규칙에 채운다. Claude Code도 쓰면 CLAUDE.md 첫 줄의 `@AGENTS.md` import를 보존·추가한다. 설치기가 CLAUDE.md를 자동 변경하지 않으므로 이 확인을 생략하지 않는다.

## 2. ai-memory 서버

출처는 [연구 자료 목록](00-research.md)의 로컬 `ai-memory/docs/install.md`다. 기존 바이너리가 없을 때 설치 담당 하네스는 플랫폼에 맞는 배포본을 설치한다. 문서화된 native 경로의 예:

```bash
mise use -g github:akitaonrails/ai-memory
ai-memory --version
ai-memory init
ai-memory serve --transport http --bind 127.0.0.1:49374
```

`serve`는 장기 실행 명령이다. 별도 서비스 터미널에서 실행하고 두 번째 터미널에서 `ai-memory status --json`을 확인한다. 이미 같은 포트의 정상 서비스가 있으면 두 번째 서버를 띄우지 않는다. mise가 없으면 원본 문서의 플랫폼별 release 설치법을 따르며 동명 crates.io 패키지를 설치하지 않는다. `cargo install ai-memory`는 이 프로젝트의 설치법이 아니다.

처음에는 provider 없는 capture·규칙 요약·FTS 경로로 검증할 수 있다. LLM consolidation/embedding은 별도 선택이다. 원격 서버를 사용한다면 `AI_MEMORY_SERVER_URL`을 해당 endpoint로 설정하고 인증은 운영 환경에서 주입한다. 일반 저장소 파일에 인증 값을 쓰지 않는다. 로컬 기본 주소는 `http://127.0.0.1:49374`, MCP 주소는 `/mcp`가 붙는다. 원격 접근은 원본 TLS/auth 지침을 따른다.

### 필드 노트 — 2026-09-26 degaza-v2 설치 (VERIFIED 실행)

- Homebrew가 있으면 `brew tap akitaonrails/tap && brew install akitaonrails/tap/ai-memory`가 mise보다 빠르다(2.4.0, 수 초). 설치 후 `ai-memory --version`으로 확인한다.
- macOS 상주 서버는 **launchd LaunchAgent가 정석**이다. 리포의 `packaging/launchd/com.github.akitaonrails.ai-memory.plist`를 sed 치환(`__AI_MEMORY_BIN__`, `__HOME__`)해 `~/Library/LaunchAgents/`에 놓고 `launchctl bootstrap gui/$(id -u) <plist>`로 등록한다. 로그는 `~/Library/Logs/ai-memory/`에 남는다. 검증: `launchctl print gui/$(id -u)/com.github.akitaonrails.ai-memory | grep state`(running) + `curl /mcp` → 405.
- 전용 터미널/백그라운드 셸의 `serve`는 셸 종료와 함께 죽어 캡처가 조용히 중단된다. 상주 서비스 없이 설치 완료로 보고하지 않는다.

## 3. ai-memory MCP와 훅 — 사용하는 하네스만

각 행의 두 명령을 모두 실행하고 하네스를 재시작한다. 실행 전 `--apply` 없는 출력으로 설정 대상과 병합 범위를 확인할 수 있다. 이때 인증 값이 출력되지 않도록 주의한다.

| 하네스 | MCP 등록 | lifecycle 등록 | 주의점 |
|---|---|---|---|
| OMP | `ai-memory install-mcp --client omp --apply` | `ai-memory install-hooks --agent omp --apply` | `.omp` MCP와 TypeScript extension. Pi와 홈을 공유하지 않는다. profile 사용 시 실제 profile 경로 확인 |
| Codex | `ai-memory install-mcp --client codex --apply` | `ai-memory install-hooks --agent codex --apply` | MCP와 훅을 따로 확인. 아래 종료 규칙 필수 |
| agy | `ai-memory install-mcp --client antigravity-cli --apply` | `ai-memory install-hooks --agent antigravity-cli --apply` | MCP `serverUrl`; 훅은 별도 hooks.json. invocation 0만 시작 경계 |
| Claude Code | `ai-memory install-mcp --client claude-code --apply` | `ai-memory install-hooks --agent claude-code --apply` | CLAUDE_CONFIG_DIR 재정의 확인. 필요 시 아래 session-aware bridge |

동시 Claude 세션은 서버 `[auto_scope] mode = "per_session"`와 `ai-memory install-mcp --client claude-code --session-aware --apply`를 함께 적용한다. 이 bridge는 Claude Code 전용이다. static MCP를 쓰는 OMP/Codex/agy 등은 모든 project-scoped 호출에 **정확한 workspace와 project**를 전달한다. 마지막 활성 프로젝트나 폴더명으로 추측하지 않는다. `.ai-memory.toml`에서 두 이름과 capture 제외 범위를 명시하고 원본 marker 문서의 형식을 확인한다. scope는 인증 권한의 대체물이 아니다.

훅 설정을 바꾼 뒤 Orca와 Mnemosyne의 기존 handler가 보존됐는지 확인한다. native/생성 extension과 legacy script의 capture 제외 지원은 같지 않다. `[capture] ignore_paths`를 모든 프롬프트·출력에 대한 완전한 비밀 제거로 간주하지 않는다.

### 종료 규칙 — Codex/agy 필수

현재 문서는 Codex CLI 0.145.0 이상이 SessionEnd를 지원한다고 설명한다. 과거 시딩 전략의 “Codex에는 없음”은 버전 차이다. Caldea는 브리프대로 최종 턴 이후 정확한 세션의 종료 확인을 의무화한다.

```bash
ai-memory finalize-session --agent codex --session-id <exact-session-id>
ai-memory finalize-session --agent antigravity-cli --session-id <exact-session-id>
```

실제 ID로 바꿔 실행한다. 이미 native 종료된 Codex 세션이면 종료·handoff 존재를 확인하고 중복 종료 대신 그 증거를 남긴다. `--all`은 다른 worker 세션을 닫을 수 있어 사용하지 않는다. Stop은 턴 경계다. finalizer 호출 성공만 보지 말고 해당 session summary와 handoff 생성까지 확인한다. 내용 없는 lifecycle-only 세션은 summary/handoff가 없을 수 있으므로 확인용 세션에는 비밀 없는 실제 작업을 포함한다.

### 기존 프로젝트 채택·라우팅

프로젝트 루트에서 순서대로 실행한다.

```bash
ai-memory bootstrap --dry-run
# 선택된 source와 provider 전송 범위를 확인하고 provider가 준비된 경우만:
ai-memory bootstrap
ai-memory install-instructions --target AGENTS.md
```

bootstrap은 LLM provider가 필요하고 한 번 수행하는 초기 수집이다. provider 미설정이면 bootstrap을 미실행으로 기록하고 기본 무LLM capture 검증을 계속한다. `--force`로 기존 manifest를 덮어쓰지 않는다. install-instructions는 ai-memory 전용 마커를 관리하므로 Caldea 마커와 기존 규칙이 함께 남아야 한다. ai-memory의 일반적인 proactive 질의 안내는 Caldea의 질문별 라우팅 경계와 함께 적용한다.

### 채택 시 필드 노트 — backfill·doctor·캡처 마커 (2026-09-26 VERIFIED 실행)

프로젝트 중반(하네스로 이미 작업한 이력이 있을 때) 채택이면 `bootstrap` 전에 backfill을 먼저 실행한다.

```bash
ai-memory backfill   # 기존 로컬 하네스 세션 저장소를 일괄 흡수. 1회성, 재실행은 no-op
ai-memory doctor     # 캡처 커버리지 검증: "N local → N captured"가 0이면 훅 문제
```

backfill은 LLM provider 없이 기존 codex/OMP 로컬 세션 기록을 흡수해 "설치 전 이력 공백"을 없앤다. 필드 결과: 22개 세션(5,782 이벤트) 흡수 후 doctor가 codex 16/16·omp 6/6 captured 확인. doctor는 §6 합격 판정의 표준 항목으로도 추가한다.

**캡처 마커는 선택이 아니라 필수다.** `.ai-memory.toml`이 없는 저장소는 훅이 설치돼 있어도 lifecycle 이벤트가 훅 프로세스에서 drop된다(스풀·전송 0 — 조용한 무캡처). 마커에 `workspace`, 필요 시 `project`, 그리고 `[capture] ignore_paths`(예: `**/*.env*`, `**/secrets/**`)를 명시하고 설치 후 doctor로 커버리지를 확인한다.

codex 첫 실행 시 훅마다 **"Hooks need review"** 신뢰 프롬프트가 뜬다. 'Trust all and continue' 선택 전까지 캡처는 시작되지 않으므로, 설치 보고에 이 사용자 액션을 남은 항목으로 명시한다.

## 4. Mnemosyne — pip·시딩·훅·MCP·스킬

Python 3.11 이상 가상환경에서 설치한다. 패키지 설치용 Python 요구 조건은 Caldea 설치기의 3.9와 다르다. 운영에서 재현하려면 검토한 release/commit으로 pin한다.

```bash
python3 -m venv /absolute/tools/mnemosyne-venv
/absolute/tools/mnemosyne-venv/bin/python -m pip install 'mnemosyne-kg[ingest,deterministic] @ git+https://github.com/tipsy-kereru/mnemosyne.git'
/absolute/tools/mnemosyne-venv/bin/mnemosyne --version
```

이후 `mnemosyne`은 위 가상환경의 실행 파일이 PATH에서 선택된다는 전제다. Orca의 새 셸에서도 같은 경로가 보이는지 확인한다.

```bash
cd /absolute/project
# 비밀·제한 원문을 제외한 수집 범위와 provider 경로를 확인한 뒤 실행
mnemosyne add . --domain coding
mnemosyne query --stats
mnemosyne wiki doctor
```

**add는 LLM 호출 가능 경로다.** API 키 제거·`--dry-run`은 offline 보장이 아니다. 허용되지 않은 소스가 섞여 있으면 `.` 대신 검토한 디렉터리를 선택한다. 외부 호출 없이 코드 구조만 추출하려면 `mnemosyne ingest extract <source.py> --domain coding --format json`을 사용한다. 이 출력이 graph DB에 저장됐다고 간주하지 않는다.

```bash
# 실제 사용하는 대상만 선택
mnemosyne config hook install codex
mnemosyne config hook install claude
# OMP/agy의 전용 Mnemosyne 훅은 문서화되지 않음: git 훅 또는 명시적 update
mnemosyne config hook install git
mnemosyne config hook status
mnemosyne config skill install --target agents
# Claude 전용 루트가 필요할 때:
mnemosyne config skill install
```

Write/Edit 훅은 `add <file>`을 실행한다. 셸 편집은 같은 훅을 보장하지 않으며 실패는 에이전트를 막지 않는다. 설치 상태와 실제 query/wiki 갱신을 각각 검사한다. 대규모 변경·브랜치 전환 후 승인된 소스에 `mnemosyne update`를 수행하고 상태를 다시 확인한다. 기존 handler와 git hooksPath/worktree 구성을 확인하고 무조건 `--force`를 사용하지 않는다.

`config hook install`은 **현재 디렉터리 기준** `.codex/hooks.json` 등에 기록한다. 반드시 대상 프로젝트 루트에서 실행하고 직후 파일 위치를 확인한다. 잘못 설치했으면 제거 명령은 `remove`다(`uninstall`은 존재하지 않는다). 필드에서 ai-memory 체크아웃 cwd에 잘못 설치해 정리한 사례가 있다(2026-09-26).

```bash
mnemosyne mcp install --client claude-desktop
mnemosyne mcp serve
```

`mcp install`은 구성 조각을 출력하는 도우미다. 클라이언트 등록을 완료했다고 보고하지 않는다. 실제 하네스의 stdio MCP 설정에 `command`를 Mnemosyne 절대 경로, `args`를 `["mcp", "serve"]`로 병합한다. `serve`는 하네스가 stdio 자식으로 실행하도록 하며 HTTP URL로 등록하지 않는다. Codex 전용 MCP 설치 도우미는 문서화되지 않았으므로 수동 등록하거나 CLI로 질의한다. OMP/agy도 각 하네스의 현행 MCP schema를 확인해 같은 stdio 명령을 연결한다.

## 5. Orca 프로젝트 등록과 managed run

```bash
orca skills get orca-cli
orca status --json
orca repo list --json
orca repo add --path /absolute/project --json
```

이미 등록된 저장소면 반환된 식별자를 사용한다. 프로젝트/호스트 가용성 등록이 필요한 경우 remote identity와 일치하는 ID로 실행한다.

```bash
orca project setup-existing-folder --project github:<owner>/<repo> --host local --path /absolute/project --kind git --json
orca worktree list --repo id:<returned-repo-id> --json
```

identity를 추측해 `local:<name>`으로 등록하거나 실패를 해결하려고 GitHub 저장소를 자동 생성하지 않는다. GUI/CLI가 반환한 정확한 project/repo/worktree ID를 사용한다. ai-memory는 Orca IDE 자체가 아니라 **내부 하네스**에 연결한다.

```bash
orca terminal create --worktree id:<repo-id>::<absolute-worktree-path> --title M1-worker --command 'ai-memory run --new M1-worker codex' --json
```

`ai-memory run omp`, `ai-memory run agy`, `ai-memory run claude`도 문서화된 선택이다. 동일 workstream의 동시 writer는 lease 충돌하므로 worker/reviewer에 서로 다른 이름을 주고 계속할 때 `--workstream M1-worker`를 사용한다. `run`은 선택적 native resume 기능이며 단순 handoff만 필요하면 직접 하네스를 시작할 수 있다. autowire는 실패해도 launch가 가능하므로 수동 연결 검증을 생략하지 않는다. 기본 예제에 권한 우회 플래그를 넣지 않는다.

Orca가 관리하는 codex-accounts 홈은 계정 브로커의 스테일 키로 첫 모델 요청에서 401이 발생할 수 있다([원인분석](knowledge/KN-2026-09-26-codex-401-stale-key.md)). 검증된 우회: 탭 커맨드를 `env CODEX_HOME="$HOME/.codex" codex ...`로 시작해 시스템 홈의 정상 ChatGPT 인증을 사용한다. 또한 codex TUI의 idle 프롬프트(`› Ask Codex to do anything`)가 보인 뒤에만 브리프를 전송한다 — trust 승인 직후 전송하면 입력이 codex가 아닌 zsh 셸로 흡수된다.

## 6. 설치 후 합격 판정

- `bash install.sh ... --check`: 스킬 bytes와 AGENTS 마커 일치.
- `ai-memory doctor`(대상 프로젝트 루트): 최근 하네스 세션이 전부 captured인지 확인. 채택이 중반이면 backfill로 과거 이력 흡수를 선행.
- `ai-memory status --json`: 선택한 서버·scope가 정상 응답. 재시작한 하네스에서 `memory_status` 실제 호출.
- 비밀 없는 테스트 턴 전후 sessions/observations를 비교하고 정확한 세션 종료 및 다음 하네스에서 handoff 수신을 확인. static MCP는 workspace/project 명시.
- `mnemosyne config hook status`: 의도한 대상만 설치. 승인된 테스트 소스를 Write/Edit 후 CLI/MCP query로 엔티티·source 변경 확인. `mnemosyne wiki doctor`의 경고도 기록.
- Orca 터미널의 cwd·하네스·입력 시작 확인. [운영 매뉴얼](workflow.md)의 dispatch receipt와 완료 계약으로 진행.

설정 파일 존재, MCP 도구 목록, 실제 capture, 실제 recall, live provider 성공을 별도 열로 보고한다. 실패 항목을 “설치 완료”로 묶지 않는다. 복구 시 타임스탬프 백업에서 해당 변경만 되돌리고 ai-memory DB·wiki·Mnemosyne 원본/graph를 삭제하지 않는다.
