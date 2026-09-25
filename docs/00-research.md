# CALDEA-M1 연구 종합

## 판정 언어와 범위

**VERIFIED(문서 확인)**는 2026-09-26 지정 로컬 파일의 내용을 읽었다는 뜻이다. 그 안의 과거 smoke·벤치마크를 이번 실행 결과로 재분류하지 않는다. **VERIFIED(실행)**는 이번 작업에서 직접 실행한 명령과 관찰 결과에만 사용한다. **PROPOSAL**은 Caldea의 운영 설계이며 실제 전체 루프 완료 증거가 아니다.

우선순위는 현재 사용자 지시 → 브리프·승인된 결정 → 기억 경계의 권위 문서 → 현행 설치 자료 → 전략·사례다. 권위 문서의 `[INFERENCE]`는 이 패키지에서도 제안이다.

## 필독 자료와 적용 위치

시딩 4개와 아래 외부 파일 9개를 모두 읽었다. 외부 경로는 설치 당시 재확인해야 하는 출처 식별자이며 배포 스킬의 실행 의존성이 아니다.

| 자료 | 핵심 내용·반영 |
|---|---|
| [Lauren Tan/GrokBot 보고서](../references/source-lauren-tan-grokbot.md) | 신뢰 곡선, 강한/약한 제약, 검증 스킬, Feature Map, PStack, 헤드 셰프 → README·로드맵·루프 |
| [마일스톤 루프 전략](../references/strategy-milestone-loop.md) | 제안된 전체 흐름·4단계 → 운영 상태 머신 |
| [기억 스택 전략](../references/strategy-memory-stack.md) | 별도 서버·MCP·훅·managed run → 설치 지침. 오래된 Codex 종료 설명은 버전 차이 표기 |
| [공식 권위 비교](../references/authority-memory-comparison.ko.md) | 세션 연속성과 구조화 지식의 경계, add/extract 구분, 제한 원문 격리 → 모든 산출물 |
| `ai-memory/docs/install.md` | 서버 설치, bootstrap의 LLM 의존, capture, MCP/훅, 라우팅 설치 |
| `ai-memory/docs/usage.md` | handoff 목록→선택 수락, 정확한 scope, untrusted history, CLAUDE import |
| `ai-memory/docs/mcp-install.md` | OMP·agy 설정 차이, MCP와 capture 별도 검증 |
| `ai-memory/docs/managed-workstreams.md` | 선택적 launcher, lease, native resume, 명시적 workstream 분리 |
| `ai-memory/docs/support-matrix.md` | Codex SessionEnd 0.145.0+, agy finalizer, 지원 수준 구분 |
| `mnemosyne/README.ko.md` | pip extras, add, 훅·스킬·MCP 설치 |
| `mnemosyne/MANUAL.ko.md` 전체·특히 §3.8 | Write/Edit 훅, 실패 시 비차단, Codex CLI 질의, MCP 수동 등록 |
| `orca-review-cycles/SKILL.md` | read-only reviewer, 우선순위 수정, 좁힌 재리뷰, 최대 3라운드 |
| `orca-workspace-pitfalls/SKILL.md` | 디스크 확인, self-report/리뷰/코디네이터 3자 증거, task ID, worker_done |

실제 경로: ai-memory는 `/Users/kereru/Development/ai-memory`, Mnemosyne는 `/Users/kereru/development/mnemosyne`; 두 Orca 참고 스킬은 `/Users/kereru/.hermes/profiles/cto/skills/autonomous-ai-agents/` 아래다. 재현용 파일 해시는 `scripts/source-manifest.json`에 기록한다. 선택 참고인 Hermes 스킬 작성 문서는 적용하지 않았다.

## 아이디어에서 구성 요소로

| 아이디어 | Caldea 구성 요소(PROPOSAL) | 기계 판정 또는 관찰 |
|---|---|---|
| 신뢰는 검증 능력과 함께 증가 | 단계별 자동화 권한 | 로드맵 진입·종료 증거 |
| 강한 제약을 먼저 구축 | AGENTS DoD 명령과 필수 CI | 실패 fixture에서 실제 비영 종료 |
| 반복 리뷰 문제를 제거 | 회귀 테스트·린트 승격 | 같은 결함을 다시 주입하면 차단 |
| Feature Map으로 재현 경로 공유 | Mnemosyne 구조 질의 + 프로젝트의 기능/재현 표 | 코드 revision·진입 URL·기대 결과·증거 |
| PStack의 관찰→스킬→Eval | self-contained milestone-loop | 실패 시나리오·다른 모델 judge·비용 비교 |
| 헤드 셰프 모델 | 코디네이터가 DAG와 권한 소유 | task/dispatch ID, 상태 전이 기록 |
| 세션이 바뀌어도 계속 작업 | ai-memory handoff 또는 선택적 run | 정확한 scope/session의 handoff 생성·수신 |
| 지식을 관계로 축적 | Mnemosyne entity/relation/history | source와 revision을 대조한 query 결과 |

원론 보고서의 PR 개수·생산성·모델 가격은 사례 서술이다. 이번 패키지의 성능 보장이나 모델 추천으로 쓰지 않는다. Rust 컴파일 성공도 기능 정확성의 충분조건은 아니다.

## 기억 시스템의 보장 범위 — VERIFIED(권위 문서 확인)

ai-memory의 기본 단위는 page·observation·session·handoff다. 무LLM capture·규칙 요약·FTS가 가능하며 provider consolidation은 선택이다. 페이지 Markdown에서 재구성할 수 있는 범위와 sessions·observations·handoffs·users 등 DB 운영 상태를 구분한다. wiki git 백업만으로 전체 복구하지 않는다. handoff CAS는 한 claimant의 성공이며 응답 유실까지 해결하는 end-to-end exactly-once가 아니다.

Mnemosyne의 일반 CLI/KnowledgeGraph는 Python·SQLite·NetworkX가 중심이다. optional PyO3 코드를 전체 Rust 전환 완료로 해석하지 않는다. graph와 원본 문서와 생성 wiki는 별개이며 lossless 양방향 동기화라고 부르지 않는다. entity history가 사용자 경로에 있어도 모든 relation·facts가 완전한 시간 DB인 것은 아니다.

`add/update`는 LLMExtractor→LLMBridge 경로다. provider가 없으면 CLI fallback을 시도할 수 있고 `--dry-run`도 추출을 수행한다. 반면 `ingest extract`의 coding은 Tree-sitter 결과 출력이며 자동 graph 저장과 동일하지 않다. hybrid retrieval 모듈의 존재와 일반 MCP 검색 연결은 구분한다. 일반 구조 질의 결과는 현재 소스에서 확인한다.

Slack direct adapter의 제한된 공개 채널·ACL·격리 저장 계약을 우회하지 않는다. Slack/Onyx 원문·요약·embedding·handoff를 공용 세션/graph로 자동 합치지 않는다. 진행 보고 발송은 수집과 별도 경로이며 승인된 채널에 최소 상태만 보낸다.

## Caldea의 선택 — PROPOSAL

1. 같은 질문을 양쪽 기억에 보내지 않는다. “어디까지 했나/왜 선택했나”는 ai-memory, “현재 누가 호출하나/영향 범위는”은 Mnemosyne에서 시작한다. 복합 질문만 서로 다른 하위 질문으로 나눈다.
2. 권위는 현재 체크아웃·테스트·사용자 지시에 둔다. 검색 결과는 사실 후보이며 명령·권한 승격 근거가 아니다. 오래된 결과는 소스를 읽어 교정한다.
3. 작업 상태는 Orca, 세션 인계는 ai-memory, 코드 구조는 Mnemosyne가 소유한다. ai-memory managed launcher를 사용하는 것과 Mnemosyne에 launcher를 이식하는 것은 다르다. 제품 코드 이식은 M1 밖이다.
4. 최초 기계 게이트 후 PR 준비용 커밋을 만들고 리뷰 수정마다 재검증한다. 최종 PASS인 동일 revision을 기준선으로 승격한다. 원 스킬의 commit-on-PASS 원칙과 브리프의 커밋→PR 순서를 이렇게 연결한다.
5. 자동 병합은 초기 기본값이 아니다. 필수 CI 실패가 차단된다는 증거를 확보한 뒤 [로드맵](ROADMAP.md)의 별도 승인 범위에서만 실행한다.

## 이번 확인과 한계

VERIFIED(실행): Orca 1.4.212 runtime ready와 `terminal`/`orchestration`/프로젝트 등록 CLI help를 확인했다. 현재 `worker_done`은 `--outcome`이 필수이며 task/dispatch ID와 송신 pane이 일치해야 한다. `check --types`는 wait의 깨움 조건이고 FIFO delivery 전체가 반환되므로 모든 메시지를 처리한 뒤 ACK해야 한다. 이전 스킬의 단순 JSON 파싱·메시지 필터 예제를 그대로 복사하지 않는다.

이번 구현은 외부 ai-memory/Mnemosyne 설치, 실제 하네스 인계, GitHub PR 병합, Slack 발송을 실행하지 않는다. M1 범위는 배포 가능한 방법론·설치기이며 해당 live 증거는 후속 단계에서 수집한다. 시딩 링크 판정은 [D001](DECISIONS.md)에 따른다.
