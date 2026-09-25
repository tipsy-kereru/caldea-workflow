# KN-2026-09-26 — Orca 탭 Codex/OMP 워커 401 "Incorrect API key" (스테일 서비스 키)

**상태:** VERIFIED (실제 격리 실험으로 원인 특정 + 해결 확인)
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
4. **격리 실험으로 원인 특정**:
   - 내 쉘에서 `codex exec` (CODEX_HOME 미설정 → `~/.codex`) → **성공** (OK-TEST)
   - `CODEX_HOME=<orca codex-accounts home>` 지정 → **401 Missing bearer** (api.openai.com) — orca 홈 자체가 아닌 상위 주입자가 범인
   - Orca가 스폰한 프로세스 → **401 sk-svcac** (chatgpt.com backend)
5. **결론:** Orca 데스크톱 앱의 codex-accounts 인증 브로커가 죽은 서비스 계정 키를 **런타임에 주입**. 디스크 어디에도 없는 키 = 앱 메모리/브로커 상태. CLI 재로그인으로는 해결 불가.

## 확정 해결 (VERIFIED)

워커 탭 커맨드에서 **시스템 codex 홈을 강제**한다 — Orca 브로커를 우회:

```bash
orca terminal create --worktree path:<project> \
  --command 'env CODEX_HOME="$HOME/.codex" codex -m gpt-6-astra -c model_reasoning_effort="high"'
```

- 적용 직후 401 제로, 워커 정상 가동 확인 (401 카운트 0)
- 부작용: Orca의 계정 관리(rate limit 브로커)를 우회 — 시스템 `~/.codex`의 ChatGPT 인증을 직접 사용

## 근본 해결 후보 (미실행 — Orca/ChatGPT 앱 업데이트 대상)

- ChatGPT 데스크톱 앱(Codex Framework)에서 완전 로그아웃→재로그인 후 Orca 재시작해 브로커 캐시 갱신
- Orca 설정에서 codex 계정 재등록

## 교훈 (워크플로우 설계 반영)

1. **워커 하네스 기동 실패는 "첫 턴 에러"로만 보인다** — 디스패치 후 401 카운트 + Working 스피너를 반드시 확인하고, 실패 시 탭을 닫고 원인부터 분리할 것.
2. **인증 오류는 4계층으로 소거**: rc/launchctl(env) → auth 파일(auth_mode) → keychain → 런타임 브로커(앱). "로그인 다시 했다"는 계층이 다르면 무용.
3. **에러 스크린의 request id를 항상 비교** — 동일하면 재발이 아니다.
4. `CODEX_HOME` 강제는 안전한 우회로: 시스템 홈의 auth가 정상임이 확인되면 즉시 적용해 진행을 막지 않는다 (root cause는 별도 이슈로 추적).
5. MCP 기동 경고(hwp-mcp→MinIO HTML, dev_manager 등)는 비치명적 노이즈 — Working 스피너 기준으로 판단할 것.