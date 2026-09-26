# KN-2026-09-26 — Orca 탭 Codex/OMP 워커 401 "Incorrect API key" (스테일 서비스 키)

**상태:** VERIFIED (기록된 격리 실험과 CODEX_HOME 강제 후 우회 성공) / INFERENCE (브로커의 런타임 키 주입이라는 내부 원인)
**심각도:** 높음 — 멀티 에이전트 워커 전면 정지
**증상 시작:** 2026-09-26 오전 (칼데아 워크플로우 M1 워커 기동 시)

## 증상

Orca 탭으로 띄운 Codex(및 OMP) 워커가 모델 첫 턴에서 401로 죽는다:

```
unexpected status 401 Unauthorized: Incorrect API key provided:
sk-svcac***…***fvMA
url: https://chatgpt.com/backend-api/codex/responses
```

- `codex login status`는 "Logged in using ChatGPT"로 정상 표시
- 사용자가 재로그인해도 **재발** (CLI/`~/.codex` 재인증은 무관)
- 여러 세션·여러 모델(gpt-6-astra, gpt-5.6-luna)에서 **동일한 죽은 키**(`sk-svcac…` — 서비스 계정 키)로 발생

## 진단 과정 (이 순서가 재사용 가능한 체크리스트)

1. **오래된 에러 스크린 구별** — 붙여넣은 401의 `request id`/`cf-ray`가 이전 에러와 동일하면 재발이 아니라 오래된 화면. (실제로 한 번은 동일 id였음)
2. **진위 판별은 로그 DB로**: `logs_2.sqlite`의 `logs` 테이블(`feedback_log_body` 컬럼)에서 `%Incorrect API%` 쿼리 + 타임스탬프. 재발 확인됨(11:35).
3. **오염원 후보 소거** (전부 깨끗):
   - 쉘 rc 파일(`~/.zshrc` 등) — export 없음
   - `launchctl getenv OPENAI_API_KEY` — 비어 있음
   - `~/.codex/auth.json` 및 Orca `codex-accounts/<id>/home/auth.json` — 둘 다 `auth_mode: chatgpt`, `OPENAI_API_KEY: null`
   - 워커 프로세스 env (`ps -p <pid> -wwE`) — OPENAI_API_KEY 없음
   - keychain (`security dump-keychain`) — openai/codex 계열 서비스에 키 없음
   - 디스크 전체 grep — 키 문자열은 로그/세션 기록에만 존재
4. **격리 실험으로 실행 경로 비교 (VERIFIED)**:
   - 내 쉘에서 `codex exec` (CODEX_HOME 미설정 → `~/.codex`) → **성공** (OK-TEST)
   - `CODEX_HOME=<orca codex-accounts home>` 지정 → **401 Missing bearer** (api.openai.com) — 다른 실행 경로와 오류/endpoint가 다름을 관찰
   - Orca가 스폰한 프로세스 → **401 sk-svcac** (chatgpt.com backend)
5. **결론:** **VERIFIED** — 실행 경로별 오류가 달랐고, 관찰한 CLI 재로그인 시도 후에도 재발했으며, 아래 CODEX_HOME 강제 후에는 관찰 구간의 401 카운트가 0이었다. **INFERENCE** — Orca의 codex-accounts 인증 브로커가 스테일 키를 런타임에 주입했을 가능성. 확인한 디스크/env에서 키를 찾지 못한 것만으로 앱 메모리·브로커의 내부 주입 경로를 확정할 수 없으며, 해당 내부 동작은 직접 관찰하지 않았다.

## 확인된 우회 (VERIFIED)

워커 탭 커맨드에서 **시스템 codex 홈을 강제**한 뒤 정상 가동을 관찰했다. 이 결과만으로 내부 브로커 우회 메커니즘까지 검증한 것은 아니다:

```bash
orca terminal create --worktree path:<project> \
  --command 'env CODEX_HOME="$HOME/.codex" codex -m gpt-6-astra -c model_reasoning_effort="high"'
```

- 적용 직후 401 제로, 워커 정상 가동 확인 (401 카운트 0)
- **INFERENCE:** 시스템 홈 선택으로 Orca의 계정 관리·rate limit 브로커 적용 경로가 달라졌을 가능성. 브로커 적용 여부는 별도 검증이 필요하다.

## 근본 해결 후보 (미실행 — Orca/ChatGPT 앱 업데이트 대상)

- ChatGPT 데스크톱 앱(Codex Framework)에서 완전 로그아웃→재로그인 후 Orca 재시작해 브로커 캐시 갱신
- Orca 설정에서 codex 계정 재등록

## 교훈 (워크플로우 설계 반영)

1. **워커 하네스 기동 실패는 "첫 턴 에러"로만 보인다** — 디스패치 후 401 카운트 + Working 스피너를 반드시 확인하고, 실패 시 탭을 닫고 원인부터 분리할 것.
2. **인증 오류는 4계층으로 소거**: rc/launchctl(env) → auth 파일(auth_mode) → keychain → 런타임 브로커(앱). "로그인 다시 했다"는 계층이 다르면 무용.
3. **에러 스크린의 request id를 항상 비교** — 동일하면 재발이 아니다.
4. `CODEX_HOME` 강제는 안전한 우회로: 시스템 홈의 auth가 정상임이 확인되면 즉시 적용해 진행을 막지 않는다 (root cause는 별도 이슈로 추적).
5. MCP 기동 경고(hwp-mcp→MinIO HTML, dev_manager 등)는 비치명적 노이즈 — Working 스피너 기준으로 판단할 것.