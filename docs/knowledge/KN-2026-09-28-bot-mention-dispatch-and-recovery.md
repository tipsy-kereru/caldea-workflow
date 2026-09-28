# KN-2026-09-28 — 봇→봇 멘션 디스패치와 리커버리 루프 (degaza-v2 실측)

**상태:** VERIFIED(실측) — 2026-09-28
**범위:** 코디네이터 봇이 QA 봇에게 검수 요청을 직접 보내고, 워커 스트림 사망·지연 메시지 오염·base 진행(리베이스) 상황을 자율 복구하는 절차. degaza-v2 Q-02 워크플로우(PR #4~#6, 마일스톤 3건 연속 merge) 실측 기반.

# 1. 봇→봇 정식 멘션 — 발송과 수신 확인

## 발송: `hermes send` 사용 (토큰 파일 열람 금지)

```bash
hermes send -t "slack:<chat_id>:<thread_ts>" "<@<상대_봇_ID>> 메시지 본문"
```

- 현재 프로필(예: cto)의 자격증명을 gateway가 재사용한다. `xoxb` 토큰을 auth.json에서 직접 추출해 curl로 보내는 방법은 **not_authed로 실패**했다(auth.json에 토큰 형식이 없음 — 원칙상 열지도 않는다).
- `hermes send --list slack`으로 대상 채널/스레드 target 형식을 먼저 확인한다.

## 봇 ID 오인 함정 — 자기 ID를 상대로 착각 금지

스레드 원문의 `<@U...>` 멘션이 "항상 상대"가 아니다. **내가 처음 보낸 메시지에 태그된 ID는 나 자신**이다.

- degaza-v2 실측: 스레드 첫 메시지에 `<@U0BPZ2FAAL8>`이 있어 Hassan ID로 착각 → 실제로는 Da Vinci(코디네이터 자신)였고, Hassan 본인 ID는 `U0BP185U71T`(상대가 auth.test로 자기 실측한 기록에서 확보).
- **검증 방법(신뢰 순):**
  1. 상대 세션 로그의 auth.test/자기 식별 기록(`gh api` 응답, 게이트웨이 로그의 "Authenticated as @handle" 연계).
  2. 수신 측 state.db의 messages에서 실제 수신된 멘션 원문 대조.
  3. 발송 후 **수신 측 gateway.log의 `inbound message` 행으로 착륙 실측** — 이것이 최종 증거다. `user=Da Vinci (CTO)`처럼 발신 봇 이름이 기록된다.
- 멘션 발송 후 수신 확인은 30~60초 내 상대 `logs/gateway.log`를 확인한다. 착륙 기록이 없으면 `allow_bots` 설정과 Socket Mode 상태를 본다.

## 운용 효과

검수 요청·판정 보고를 사용자 중개 없이 봇끼리 주고받을 수 있다. 사용자 멘션 병목이 제거되면 리뷰 라운드가 자율로 돈다.

# 2. 모니터 스크립트 — 완료·판정 감지 설계

백그라운드 모니터는 "한 가지 조건 + 타임아웃 래핑"으로 만든다.

- **모든 명령을 `timeout N`으로 래핑**한다. unwrap된 명령 하나가 Hangup하면 모니터 전체가 묵모 사망한다(실측: 8시간 표시의 좀비 모니터).
- **지연 메시지 오염 방지 — from_handle 필터**: Orca inbox에는 이전 워커의 worker_done이 `current_delivery` 계약으로 늦게 도착한다. 발신자 핸들을 비교해 현재 워커 것만 채택한다(실측: 이전 워커 지연 메시지를 2번 잡아 오탐).
- **디스크 이중 감지**: `git ls-remote --heads origin <branch>`로 push 감지 + inbox worker_done 감지를 병행. 둘 중 하나만 살아도 감지된다.
- 감지 성공/타임아웃을 출력 첫 단어(`PUSHED:` / `INBOX_MSG:` / `PR_ACTIVITY:` / `TIMEOUT_...`)로 구분해 코디네이터가 파싱 쉽게 한다.
- 장기 감시 대상(리뷰 판정 등)은 `gh pr list --json number,reviews,comments,mergedAt`을 60초 주기로 폴링하고, 대상 PR 번호만 필터링한다.

# 3. 리커버리 루프 — 끊김·실수·레이스의 실측 복구 사례

## A. 워커 스트림 사망 ("Connection reset by peer")

1. 터미널 read로 사망 시점 확인 → worktree `git status`로 커밋 전 상태인지 확인(깨끗하면 손실 없음).
2. 브리프 재전송(`orca terminal send --enter`)으로 같은 pane 재개. 커밋 후 사망이었으면 push 상태부터 확인하고 재작업 범위를 줄인다.

## B. 디스패치 오배정 (브리프가 잘못된 탭으로 감)

1. 즉시 해당 탭에 취소 지시 전송("아무것도 쓰지 말고 브리프 무시, 수정했다면 revert, idle 대기").
2. 잘못된 worktree의 `git status`로 오염 여부 확인 → 깨끗하면 종료.
3. 올바른 워커 탭에 브리프 재전송. **task 라이프사이클 추적이 잘못된 탭에 걸려도 실제 결과는 커밋 SHA로 검증**한다(추적 메타데이터가 공갈 증거가 되지 않게).
4. 예방: dispatch 전 워커 탭-태스크 매칭을 이중 확인(터미널 title/worktree 경로 대조).

## C. PR base 진행 — 리베이스 레이스 (병렬 PR의 필연 코스)

병렬 PR 2건이 있으면 먼저 머지된 PR이 나머지의 base를 바꾼다.

1. 머지 전 `gh pr view <n> --json mergeable,mergeStateStatus`로 확인(UNKNOWN이면 15초 후 재조회).
2. 머지된 base를 `git fetch origin && git rebase origin/main`으로 흡수 → **force-with-lease push**(일반 force 금지).
3. 리베이스로 커밋 SHA가 바뀌면 **Hassan 판정의 "읽은 SHA"와 달라진다** — 이때는 판정의 "재리뷰 범위" 지시를 따른다. degaza-v2 실측: "docs 게이트 재실행 결과만 재확인" 조건이었으므로 head에서 `tools/check_docs.py` 재실행(exit 0, errors 0) + 증거 파일 커밋으로 동일 revision 요건을 충족했다.
4. 재실행 증거는 검증 문서(wiki/verifications/...)로 커밋해 판정·재실행·merge 3요건의 사슬을 남긴다.

## D. 판정 뒤 merge 조건이 붙은 경우

CONDITIONAL PASS/PASS-with-conditions는 **조건 이행 증거를 커밋으로 남긴 뒤** merge한다. merge 게이트 3요건(QA PASS / 동일 revision 증거 / 사용자 승인)의 충족 근거를 판정 코멘트에 대응시켜 기록한다.

# 4. 실측에서 나온 기타 규칙

- **거래 메타데이터 오독 금지**: PR 판정에서 "exit 0 = receipt 완료(공급자 성공 아님)"처럼, 게이트 결과의 의미를 도구 docstring 수준에서 정확히 구분해 코디네이터 오독을 막는다.
- **Slack API 직접 호출 금지**: 코디네이터는 Slack API를 못 쓴다(게이트웨이가 못 받는다). 발신은 `hermes send`, 판정 읽기는 `gh pr view`, 수신 확인은 상대 gateway.log로 한다.
- **판정 지연이 반복되면**: 상대 봇의 Socket Mode 재접속 로그를 확인하고, 게이트웨이 재시작은 사용자에게 요청한다. 재시작 직후 첫 멘션이 정상 수신되는지 실측한다.
- **마일스톤마다 메모리 갱신**: ai-memory 인계 페이지에 커밋·PR·판정·merge·잔여 위험을 누적 기록한다. 세션이 압축돼도 커밋 SHA 사슬로 복원 가능해야 한다.
