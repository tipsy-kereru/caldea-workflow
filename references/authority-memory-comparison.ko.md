# ai-memory와 Mnemosyne 비교 및 기술 이식 검토

**조사일:** 2026-09-26  
**범위:** 로컬 두 저장소의 문서·실제 구현·격리된 실행 경로. 제품 전체 품질 평가나 성능 벤치마크는 아니다.

| 프로젝트 | 조사 경로 | 선언 버전 | 조사 시 HEAD |
|---|---|---|---|
| ai-memory | `/Users/kereru/Development/ai-memory` | Cargo workspace `2.4.1` | `433a19f3d54dea287571b1423591db2a89965fa9` |
| Mnemosyne | `/Users/kereru/Development/mnemosyne` | Python package `0.11.0` | `12215e23427fec7aaa407c6a5b9c3403ef9efd20` |

HEAD는 식별용이다. 실제 판단 기준은 조사 당시 작업 트리의 파일이며, 커밋과 작업 트리의 일치를 보증하지 않는다. 아래 **구현 확인**은 소스에서 실행 경로를 확인했다는 의미이고, **실행 확인**은 §7의 smoke에서 직접 관찰한 범위에만 사용한다. 설계 제안·미검증 위험은 `[INFERENCE]`로 구분한다.

## 1. 결론

**ai-memory는 “에이전트 작업의 연속성”, Mnemosyne는 “여러 도메인의 구조화된 지식 축적”에 최적화되어 있다. 두 프로젝트는 대체재라기보다 서로 다른 중심을 가진 인접 시스템이다.**

- **ai-memory:** 프롬프트·도구 실행·세션 종료를 자동 수집하고, 위키 페이지와 인수인계 상태로 바꾼다. 다른 에이전트·기기·사용자가 같은 프로젝트에서 작업을 이어가는 것이 제품의 중심이다.
- **Mnemosyne:** 문서·코드에서 엔티티와 관계를 추출하고, SQLite 지식그래프·시간 이력·Markdown wiki로 축적한다. coding/daily/legal 도메인, 코드 구조, 개인 문서와 외부 지식원의 경계가 중심이다.
- **권고 [INFERENCE]:** Mnemosyne의 그래프를 ai-memory의 페이지 저장소로 교체하지 않는다. 대신 **안전한 수집 경계, 무LLM 세션 요약, 원자적 handoff, 제한된 시작 컨텍스트, 검색 설명·평가**를 가져온다.
- **우선순위 [INFERENCE]:** 새 기능을 복사하기 전에 기존 `ingest`/`extraction` 경로와 독립 `retrieval` 모듈의 통합 상태를 바로잡아야 한다. RRF, facts, jobs, Rust 소스가 이미 있다는 사실과 사용자 경로에 연결되어 있다는 사실은 다르다.
- **전체 Rust 전환·dream 자동 재작성·managed launcher 전체 이식은 후순위 [INFERENCE].** 현재 필요한 계약보다 큰 운영 표면을 함께 가져오기 때문이다.

근거: [A1], [A2], [M1], [M2], [M3], [M4].

## 2. 각자의 설계 방향

### 2.1 ai-memory: 세션을 읽을 수 있는 기억으로 컴파일

기본 흐름은 다음과 같다.

1. 에이전트 lifecycle hook/native spool이 이벤트를 수집한다.
2. capture policy와 sanitizer가 수집 제외·비밀 제거·크기 제한을 적용한다.
3. bounded writer가 SQLite에 observation/session 상태를 기록한다.
4. SessionEnd에서 규칙 기반 `sessions/<id>.md`와 자동 handoff를 만든다.
5. 다음 에이전트는 검색 또는 명시적으로 활성화한 시작 컨텍스트로 기억을 사용한다.
6. provider를 설정한 경우에만 LLM consolidation 등의 추가 경로가 동작한다.

**기억의 기본 단위는 페이지와 세션이다.** 엔티티 인덱스는 페이지 frontmatter의 명사를 검색하기 위한 보조 구조이며, Mnemosyne의 함수·사람·의무 등 typed entity/relation 모델과 같지 않다. Rust workspace가 store/wiki/hooks/MCP/LLM/consolidation/workstream 등을 분리하고, 한 writer thread가 SQLite 쓰기 연결을 소유한다. CLI의 `search`도 로컬 DB를 직접 읽는 명령이 아니라 서버 HTTP API의 클라이언트다. [A2] [A3] [A4] [A5]

#### 원본 저장소의 경계

“Markdown가 source of truth, SQLite는 derived index”라는 소개는 **페이지 내용**에는 맞지만 **시스템 전체**에는 불완전하다.

- 위키와 `_meta.md`로 페이지·프로젝트 식별자·검색 인덱스를 재구성할 수 있다.
- `reindex`는 **sessions, observations, handoffs, users, audit rows, decay counters**를 Markdown에서 복구하지 않는다. embedding도 별도 재계산이다.
- 따라서 위키 git 백업만으로 운영 상태를 복구할 수 없다. DB snapshot이 필요하다.
- 파일 교체와 SQLite update는 서로 다른 자원이다. wiki write는 경로별 lock·파일 rollback을 사용하지만, 두 자원을 하나의 ACID transaction으로 만드는 것은 아니다.

이 구분은 이식 시에도 유지해야 한다. [A6] [A7]

### 2.2 Mnemosyne: 엔티티·관계·출처를 축적하는 지식그래프

현재 사용자 경로의 중심은 Python이다.

1. `ingest add/update`는 파일·URL·텍스트를 읽어 `LLMExtractor → LLMBridge`로 보낸다.
2. 추출된 엔티티·관계를 SQLite에 병합하고 entity history·출처·충돌 정보를 남긴다.
3. 선택적으로 graph에서 entity/source Markdown wiki를 생성한다.
4. `graph query`, HTTP/MCP가 구조화 질의와 entity FTS 검색을 제공한다.
5. 별도 `ingest extract`는 coding 도메인에서 Tree-sitter 결과를 출력한다. `ExtractionPipeline`이라는 별도 다층 추출 API도 있다.

`KnowledgeGraph`는 `sqlite3`를 직접 사용하고, WAL·읽기 connection pool·NetworkX `DiGraph`를 가진다. 시작 시 DB에서 NetworkX 그래프를 구성한다. entity update는 버전과 history를 남기지만 relation update의 version만으로 과거 관계 전체를 재구성할 수 있는 것은 아니다. [M2] [M3] [M5]

**원본 문서, 구조화된 graph, 생성 wiki의 역할이 다르다.** 현재 Obsidian 운영 문서는 사람이 관리하는 Markdown을 원본으로 두고 DB/raw를 동기화 Vault 밖에, 생성 wiki를 별도 위치에 둘 것을 요구한다. `wiki rebuild`는 graph에서 생성 영역을 재생성하며 수기 영역 보존 로직이 있다. Wiki Markdown 재수집은 가능하지만, lossless 양방향 entity/relation 동기화와 동일하지 않다. [M6] [M7]

#### 지향 아키텍처와 현행 구현을 구분

루트 `ARCHITECTURE.md`는 명시적으로 **Design Phase** 문서다. Rust core 70–80% / Python subagent 20–30% 등은 목표 구조이지 현재 실행 비율이 아니다. `mnemosyne-core`에는 PyO3 graph/DB/wiki 함수가 존재하지만 일반 `KnowledgeGraph`/CLI 경로는 Python SQL·NetworkX를 사용한다. “이미 Rust core로 전환 완료”라고 해석하면 안 된다. [M8]

## 3. 기능·구조 비교

| 축 | ai-memory | Mnemosyne | 의미 |
|---|---|---|---|
| 주사용자 문제 | 에이전트·세션·기기 사이 작업 연속성 | 문서·코드·개인 지식의 구조화·연결 | 에이전트 기억과 도메인 지식은 동일한 모델이 아님 |
| 기본 기억 단위 | wiki page, observation, session, handoff | entity, relation, scope, entity history; 생성 wiki | schema 그대로 복사하기보다 변환 계약 필요 |
| 구현 중심 | Rust/Tokio/Axum, rusqlite, git2 | Python/sqlite3/NetworkX, optional PyO3 | Rust 도입 자체보다 저장 불변조건이 이식 대상 |
| 무LLM 경로 | capture·규칙 세션 요약·FTS·handoff | coding Tree-sitter extract·graph CRUD/query·wiki rebuild | `ingest add`는 별도 LLM 경로임 |
| 일반 문서 추출 | lifecycle 관측의 compilation이 중심; LLM consolidation은 선택 | add의 LLM bridge, 별도 semantic/local-model 계층 | zero API cost와 zero LLM/network는 구별 |
| 코드 이해 | 도구 실행·파일 경로·결정의 작업 기록 | 함수·클래스·import/call 구조 추출 | 코드 구조 분석은 Mnemosyne 유지 |
| 검색 | 페이지 FTS/entity/link RRF + 선택적 vector; authority·explain | 실제 CLI/MCP는 KG/FTS; 별도 hybrid engine에 BM25/vector/graph RRF | Mnemosyne는 hybrid의 실제 연결부터 필요 |
| temporal | 페이지 supersession, ingestion validity, as-of 관련 구현 | entity history/tombstone, 별도 FactsStore validity | 양쪽 모두 “모든 데이터의 완전한 bitemporal DB”로 부르지 않음 |
| 충돌·중복 | content hash/version, lint·opt-in dedup/compaction | ID 기반 병합, property conflicts, wiki contradiction review | 의미적 동일성 판정과 ID upsert는 다름 |
| 세션 인수인계 | owner/scope/receiver 검증과 open→accepted CAS | project/session scope는 있으나 대응하는 claim-once handoff 제품 경로는 확인되지 않음 | ai-memory의 가장 직접적인 기능 이식 후보 |
| hooks | 다수 harness의 lifecycle capture; 지원 수준은 hooks/MCP/managed-only로 구분 | git/Claude/Codex/Gemini/Copilot 파일 변경 중심 hook | 지원 개수보다 이벤트 의미와 실패 처리가 중요 |
| wiki 운영 | Markdown/git authority, watcher, versioning, reindex | graph→wiki 생성·재생성, 생성 영역/수기 영역 구분 | graph를 버리고 file-first로 전환할 필요 없음 |
| 기억 수명 | episodic decay·접근 강화; TTL·선택적 compaction/dream | retention 및 wiki budget 코드, entity tombstone/history | 접근 빈도 측정·가역성·정책 우선순위 강화 여지 |
| 외부 지식 통합 | 에이전트/MCP/server 운영에 집중 | Obsidian/Joplin 표면, Onyx/Slack 전용 계약·격리 | Mnemosyne의 기존 정보 경계를 보존해야 함 |
| 공유 운영 | workspace/project, 사용자/API credential, owner, audit, 웹 UI | 로컬 graph+HTTP/MCP, scope/channel, 통합별 ACL gate | scope를 authentication/authorization과 혼동 금지 |
| 배포 | 단일 Rust binary, server·서비스·컨테이너 패키징 | Python package, CPython 포함 binary 배포, optional ML/native deps | 실행·모델·배포 의존성 범위가 다름 |
| 품질 평가 | live-server retrieval harness, hit/recall/latency/context 지표 | 다수 기존 테스트·benchmark 자산; 이 조사에서 공통 품질 비교 미실행 | 테스트 개수·서로 다른 벤치마크 숫자로 우열 판단 불가 |

근거: [A1]–[A12], [M1]–[M13]. UI·배포·외부 harness 전체는 실행 검증하지 않았다.

## 4. 현재 상태를 잘못 판단하기 쉬운 지점

### 4.1 Mnemosyne의 add와 extract는 다른 경로

- `Ingester._add_file`은 코드 확장자이면 domain을 `coding`으로 바꾸지만, Tree-sitter로 자동 전환하지 않고 `LLMExtractor.extract_file`을 호출한다.
- `LLMBridge._detect_provider`는 환경 설정/API key를 보고 provider를 선택하며, 없으면 CLI 경로를 사용한다. provider 실패 후에도 CLI fallback을 시도한다.
- 따라서 **“API key를 지우면 add가 offline deterministic으로 동작한다”는 가정은 틀리다.** `--dry-run`도 추출을 먼저 수행하므로 외부 호출 방지 옵션이 아니다.
- `ingest extract`의 coding 경로는 Tree-sitter를 사용한다. 이 CLI의 daily/legal은 아직 구현되지 않았다는 메시지로 종료한다. 별도 pipeline/semantic 모듈의 존재와 구분해야 한다.
- `[INFERENCE]` `LLMExtractor`가 extraction error를 경고만 남기고, `Ingester`가 이후 file hash를 기록하는 경로는 실패 후 재수집을 skip할 위험이 있다. 이번 조사에서 실제 provider 실패를 유발해 검증하지는 않았다.

**이식 시 결정 [INFERENCE]:** provider policy와 추출 전략을 명시적으로 선택하고, 실패한 추출을 성공 checkpoint로 기록하지 않는 계약이 먼저다. 새로운 Tree-sitter 구현은 필요하지 않다. [M3]

### 4.2 hybrid retrieval은 구현 존재와 서비스 연결을 분리해야 함

`retrieval/engine.py`에는 RRF와 cache가 있지만, MCP `_search`는 `kg.query("search:...")`를 호출한다. 소스 조사에서 일반 CLI/MCP 검색이 이 hybrid engine으로 들어가는 경로는 확인되지 않았다.

또한 현재 엔진에는 다음 제약이 있다.

- `_graph_augment`와 `_rerank`는 입력을 그대로 반환하는 placeholder이다.
- `_run_strategies`는 주석과 달리 순차 반복이다.
- 메모리 cache key에는 filters가 없고, persistent cache key에는 scope/mode가 없다.
- `query(scope_id=...)`의 scope가 strategy filters에 자동 병합되지 않는다.
- cache invalidation helper의 주석은 KG write 후 연결을 후속 작업으로 남긴다.

`[INFERENCE]` 이 상태로 단순히 MCP에 연결하면 검색 scope·filter 격리와 최신성 문제가 노출될 수 있다. **RRF를 또 만드는 것이 아니라 기존 엔진을 안전하게 완성·연결하는 작업**이어야 한다. 이 항목은 정적 구현 근거이며 이번 smoke에서 교차-scope 유출을 재현했다는 뜻은 아니다. [M4]

### 4.3 시간 이력·작업 큐 역시 연결 상태를 구분

- `KnowledgeGraph.entity_history`는 사용자 경로에 연결되어 있다. 실행으로 update 후 version 2와 history 두 개를 확인했다.
- `FactsStore`는 validity interval·supersession·history API를 제공하지만, 일반 ingest가 이를 자동 채우는 경로는 확인되지 않았다.
- `JobQueue`는 SQLite 기반 submit/acquire/complete/fail primitive이지만, 실제 worker/CLI consumer 연결은 확인되지 않았다.
- wiki budget의 access-frequency 항은 현재 상수다. 실제 접근 횟수에 따른 강화가 이미 완성되어 있다고 볼 수 없다.

새 facts/queue/cache 체계를 병렬로 추가하기보다 기존 모듈의 역할과 소비자를 확정하는 편이 낫다. [M9] [M10]

### 4.4 ai-memory의 가역성·정확히 한 번 보장을 과장하지 않음

- handoff CAS는 DB에서 **한 claimant만 성공**하게 한다. commit 뒤 응답 유실까지 해결하는 end-to-end exactly-once delivery는 아니다.
- 일반 페이지 수정/compaction의 supersession은 이전 버전을 남기지만, TTL 삭제·decay ancestry purge·선택적 raw observation prune 경로도 있다.
- raw observation을 지우면 그 입력으로 더 좋은 모델의 재consolidation을 할 수 없다.
- sanitizer의 observation 타입 경계가 모든 text field·handoff·path까지 자동 보장하는 것은 아니다. secret 제거와 prompt-injection 방어는 별도다.

이식 문서에는 “절대 삭제하지 않음”, “모든 비밀 제거”, “전송 정확히 한 번” 대신 실제 보장 범위를 적어야 한다. [A8] [A9] [A10]

### 4.5 Onyx/Slack은 live 운영 승인과 구현 완료가 다름

Mnemosyne의 Onyx mapper/exporter에는 classification·visibility·ACL freshness·tombstone 등의 enforcement가 구현되어 있다. 그러나 실제 destination capability/ACL, provider/privacy, withdrawal와 live preflight 승인은 별도 gate다.

직접 Slack adapter는 기본적으로 non-loopback 호출을 거부한다. 현재 공개 채널만 허용하고 private/DM/shared 채널 및 missing/stale ACL을 거부한다. direct Slack content는 일반 graph가 아니라 격리된 `slack_*` 저장 경로를 사용하며 `work-slack`은 일반 graph read에서 제외한다.

**ai-memory식 공용 session memory에 Slack/Onyx 원문을 자동 합류시키면 안 된다 [INFERENCE].** 요약·embedding·handoff·검색 cache도 원본의 공개 범위와 삭제 정책을 상속해야 한다. [M7] [M11] [M12]

## 5. ai-memory에서 가져올 기술: 우선순위와 적용 지점

아래는 **설계 권고 [INFERENCE]**이며 이번 조사에서 구현한 기능 목록이 아니다. 난도는 상대적인 변경 표면이며 일정 추정이 아니다.

| 순서 | 후보·가치 | ai-memory 근거 | Mnemosyne 적용 위치 | 난도·주요 위험 |
|---|---|---|---|---|
| P0-1 | **수집 전 sanitizer + 저장 진입점 계약**: 비밀·제어문자·크기 제한을 저장보다 앞에 둠 | `core/sanitize.rs`, `Wiki::write_page` [A8] | `ingest/llm_bridge.py`, `ingester.py`, `hooks/`, MCP ingest, 기존 통합 redaction | 중. 원문 보존과 정제본 저장을 구분; 오탐 손실·누락·provider 전송 전 적용 여부 |
| P0-2 | **실제 검색 경로 기반 평가**: hit@k와 recall@k 분리, evidence 중복 제거, latency/context 동시 측정 | `evals/src/retrieval/score.rs` [A11] | 기존 `scripts/bench/`, retrieval/CLI/MCP 검증 경로 | 중. 한국어·코드·legal·ACL fixture 필요; synthetic 점수 일반화 금지 |
| P1-1 | **무LLM lifecycle compilation + 멱등 이벤트 처리** | `hooks/synth.rs`, ingest-key·SessionEnd transaction [A2] [A9] | `hooks/`, `ingest/`, `jobs/queue.py`, `wiki/llm_wiki.py` | 중~상. capture 동의, 성공 checkpoint, 종료 재전송·중간 crash 처리 |
| P1-2 | **typed handoff + CAS claim**: 단순 session scope와 별개인 인수인계 상태 | `accept_handoff_in_transaction` [A9] | graph DB의 새 handoff 상태, `mcp/tools.py`, 세션 시작 hook | 중. owner/scope/receiver 일치, 응답 유실, 수명·취소 계약 |
| P1-3 | **예산 제한 시작 brief**: 필요한 기억만 신뢰 경계와 함께 주입 | `hooks/router.rs` renderer [A12] | 기존 wiki context/budget, MCP 또는 시작 hook | 중. 한국어 UTF-8 bytes≠문자≠token; pinned 과다·오래된 사실 |
| P1-4 | **RRF 설명·bounded authority를 기존 엔진에 통합** | `store/reader.rs` hybrid/explain [A5] | `retrieval/engine.py`, `strategies/`, KG FTS, MCP search | 상. 먼저 scope/filter/cache invalidation을 통일; authority의 관련성 왜곡 |
| P1-5 | **hash+canonical metadata 기반 revision·provenance** | `store/ops.rs` page upsert/supersession [A13] | 기존 entity history·ingest conflict·FactsStore·source metadata | 중~상. 같은 내용의 새 증거와 새 content version 구분; ID 충돌·출처 삭제 |
| P2-1 | **bounded single-writer + transaction 경계** | `store/writer.rs` [A4] | `KnowledgeGraph` write 및 기존 queue/읽기 pool | 상. 긴 write의 queue 정체, DB/NetworkX 동기화, 다중 프로세스 소유권 |
| P2-2 | **접근 강화 + 가역적 episodic compaction** | `decay.rs`, `sweep.rs` [A10] | `wiki/budget.py`, retention, entity tombstone/history | 상. 인기 편향, 법률 증거 보존, TTL과 pin 충돌; 먼저 score-only 도입 |
| P2-3 | **페이지 revision/checkpoint와 복원 절차** | `Wiki::write_page`, `reindex`, online backup [A6] [A7] | wiki 생성·DB backup·원본/수기 영역 관리 | 중. git에 비밀 영구 잔존; wiki만으로 DB 운영 상태 복원 불가 |

### 5.1 P0: 안전 경계와 평가부터

**sanitizer 이식 방식 [INFERENCE]**

- Rust `Sanitized<NewObservation>`의 핵심은 언어가 아니라 “정제되지 않은 관측을 저장 API가 받지 않는다”는 제약이다. Python에서는 중앙 factory/검증된 payload와 단일 저장 진입점으로 구현한다.
- provider 호출 **전**, spool 기록 **전**, error log **전**의 경계를 따로 확인한다. DB 직전에만 정제하면 외부 전송과 로컬 spool의 원문 유출을 막지 못한다.
- 기존 Slack/Onyx redaction·ACL 코드를 우회하지 않는다. 모든 source를 하나의 덜 엄격한 sanitizer로 대체하지 않는다.
- 기본 원문을 임의로 파괴하지 말고 원본의 보존 정책과 파생 observation의 정제 정책을 분리한다. capture가 허가되지 않은 원문은 원본/정제본 모두 새로 저장하지 않는다.
- secret regex 오탐·미탐, allowlist 과면제, UTF-8 절단, instruction-like history를 포함하는 fixture로 검증한다.

**평가 이식 방식 [INFERENCE]**

공통 질의 집합에서 KG FTS baseline과 hybrid 후보를 **동일 scope·동일 corpus·동일 반환 예산**으로 비교한다. 최소 지표는 hit@k, recall@k, p50/p95 latency, 실제 또는 명시적으로 추정된 token 수, ACL 위반 건수, stale/deleted 결과 건수다. 문서 chunk 여러 개가 같은 출처를 반복해 recall을 부풀리지 않게 한다. LLM judge는 선택 기능이며, 근거 검색 평가와 답변 생성 평가를 분리한다.

### 5.2 세션 기억을 graph와 연결하되 섞어버리지 않음

**제안 계약 [INFERENCE]**

- observation: `event_id`, `session_id`, `scope_id`, `source_channel`, `actor`, 시각, 정제된 bounded body, processing state.
- handoff: owner·source/receiver session·scope·state·summary·next steps·evidence references. 프로젝트 지식 공유와 개인 handoff 전달 범위를 분리한다.
- observation 기록과 dedup key를 같은 transaction에 넣고, 후속 wiki/handoff 완료 여부를 따로 관리한다. event 수신 성공과 모든 파생 작업 완료를 혼동하지 않는다.
- SessionEnd의 규칙 요약은 LLM 실패와 무관하게 존재해야 한다. LLM이 의미를 더하는 경로는 별도 승인/설정으로 둔다.
- 장기 graph에 승격할 결정·오류 원인·사실은 observation/source의 증거 참조를 유지한다. 모든 도구 출력을 지식 사실로 승격하지 않는다.
- 시작 brief는 현재 task, 확정 결정, 미해결 질문, 필요한 entity/source 링크만 선별한다. 예산 초과 자료는 링크로 남기고 untrusted-history 경계를 잘라내지 않는다.

ai-memory의 handoff는 응답을 조립한 후 claim하며, 관련 startup cursor와 claim을 같은 writer transaction에서 다룬다. Mnemosyne도 “읽고 나서 나중에 accepted로 갱신”하는 경쟁 조건을 피해야 한다. 다만 네트워크 수신까지 exactly-once가 필요하면 별도의 ACK/recovery 계약을 설계해야 하며, CAS만 복사해서 해결됐다고 하면 안 된다. [A9] [A12]

### 5.3 검색 이식은 알고리즘 추가보다 통합 작업

**권장 순서 [INFERENCE]**

1. `scope_id`, source channel, visibility/ACL, temporal validity를 모든 strategy와 cache에 같은 계약으로 전달한다.
2. 메모리·persistent cache key를 query/scope/filter/mode/index revision 기준으로 일치시키고 mutation 시 무효화한다.
3. CLI/MCP의 명시적인 검색 모드에서 기존 `RetrievalEngine`을 호출한다. 일반 KG 구조화 질의는 유지한다.
4. FTS·vector·graph candidate별 기여와 RRF·authority 조정을 explain에 남긴다. 동점은 결정적으로 정렬한다.
5. 실제 모델이 없는 경로와 모델이 있는 경로를 각각 평가한다. 외부 provider 장애를 기본 lexical 검색 장애로 전파하지 않는다.

ai-memory의 기본 RRF는 rank별 `1/(60 + rank)`를 합치므로 서로 다른 점수 스케일을 직접 비교하지 않아도 된다. 그러나 Mnemosyne에도 같은 계열의 fusion이 이미 있다. **가져올 핵심은 또 하나의 RRF 함수가 아니라 production routing·explain·bounded authority·평가 계약이다.** [A5] [M4]

### 5.4 바로 가져오지 않을 것

| 대상 | 보류 이유 | 재검토 조건 |
|---|---|---|
| graph를 버리는 file-first 전환 | entity identity·관계·history·Onyx 계약을 동시에 바꿔야 함 | file-first가 명시적 제품 목표일 때 별도 migration 설계 |
| managed workstream 전체 | launcher, native transcript adapter, lease, cursor, repository/worktree identity까지 별도 제품 범위 | 단순 handoff보다 강한 cross-harness resume가 실제 요구될 때 |
| dream/LLM cold-cluster rewrite | embedding+LLM 의존, 과병합·출처 손실 위험. ai-memory도 기본 off | recall/evidence 보존 gate, 취소·복원 절차 확보 후 |
| 팀 인증·웹 UI 전체 | 개인 graph 조사에서 team server를 새 목표로 만들 이유 없음 | 배포·사용자·권한 모델 요구가 확정될 때 |
| 전면 Rust 재작성 | 기존 optional Rust와 Python 경로의 계약부터 불명확 | 실제 CPU/메모리/쓰기 병목 측정과 parity 기준 확보 후 |

## 6. 단계별 실행 제안과 완료 조건

이 절은 후속 구현 계획이며, 이번 문서 작성 작업에 포함된 변경은 아니다. [INFERENCE]

| 단계 | 수행 범위 | 완료 조건 |
|---|---|---|
| 0. baseline·계약 | 실제 ingest/search 경로, provider policy, scope/ACL/출처/삭제 규칙, 평가 corpus 고정 | offline 경로에서 외부 호출 없음; scope·filter 간 cache 오염 없음; 현재 FTS 지표 재현 |
| 1. 안전한 capture | sanitizer와 bounded event, 기존 queue를 소비하는 worker, deterministic session summary | 중복 이벤트가 관측을 늘리지 않음; 실패 추출이 성공 hash가 되지 않음; crash 후 미완료 파생 작업 식별 |
| 2. continuity | handoff CAS, owner/scope 검증, bounded brief | 동시 claimant 중 한 명만 성공; 다른 owner/scope 거부; multibyte/신뢰 경계 보존; 응답 유실 의미 문서화 |
| 3. recall | hybrid를 실제 CLI/MCP에 연결, explain·authority, cache invalidation | baseline 대비 합의된 recall·latency·context 기준 충족; 삭제·ACL 변경이 결과에서 제거 |
| 4. 가역적 유지관리 | evidence-aware revision, 접근 점수, opt-in compaction/checkpoint | 원본·수기 영역 보존, 복원 가능, 보존 대상 법률/업무 증거 제외, DB+wiki 복구 훈련 |

**첫 구현 묶음 권고:** 단계 0과 1의 일부인 “명시적 무LLM 수집 경로 + provider 전송 전 privacy gate + 성공 checkpoint 계약 + 작은 recall baseline”. handoff는 그 다음이다. 기반 수집이 조용히 누락되면 정교한 handoff/검색도 잘못된 기억을 전달한다.

### 코드·알고리즘 재사용 방식과 라이선스

ai-memory는 MIT이며 `LICENSE`의 저작권·허가 고지 보존 조건을 따른다. Mnemosyne도 package metadata상 MIT다. 코드나 상당 부분을 복사하면 원 저작권·라이선스 고지를 포함하고, 가져온 원본 revision·변경 범위를 기록해야 한다. 알고리즘·불변조건을 Python으로 재구현하는 경우에도 출처를 남기는 편이 추적에 유리하다. [A14] [M1]

**권고 [INFERENCE]:** Rust crate 전체 의존성보다 작은 계약/알고리즘을 현행 모듈에 통합한다. 특히 기존 `FactsStore`, `JobQueue`, `RetrievalEngine`, PyO3 core와 동일 목적의 두 번째 체계를 만들지 않는다.

## 7. 이번 조사에서 실제 실행한 검증

모든 데이터는 `TemporaryDirectory` 안의 synthetic source/DB/wiki였다. 기존 개인 Vault·전역 graph·외부 Slack/Onyx를 읽거나 수집하지 않았다. ai-memory 서버는 임시 HOME와 data-dir, loopback 전용 포트, provider 없는 환경, embedding `none`, watcher off로 실행했다. 테스트 suite나 품질 benchmark는 실행하지 않았다.

### 7.1 Mnemosyne

실행 명령/API:

```text
.venv/bin/python -m mnemosyne.cli --help
.venv/bin/python -m mnemosyne.cli ingest extract <tmp>/sample.py --format json --scope-id comparison-smoke
KnowledgeGraph(<tmp>/knowledge.db): create_scope → add_entity ×2 → add_relation → update_entity → close/reopen
.venv/bin/python -m mnemosyne.cli graph query 'entity:function[normalize_name]' --db-path <tmp>/knowledge.db --global
.venv/bin/python -m mnemosyne.cli wiki rebuild --db-path <tmp>/knowledge.db --wiki-root <tmp>/wiki --format json
.venv/bin/python -m mnemosyne.cli wiki doctor --db-path <tmp>/knowledge.db --wiki-root <tmp>/wiki --format json
```

관찰 결과:

- Tree-sitter가 synthetic Python의 `normalize_name`, `greet` 두 함수를 추출했다. 각 결과에 `extraction_method: tree-sitter`가 있었다.
- **graph 입력은 별도 직접 API 호출**이었다. extract CLI가 자동으로 이 DB에 저장했다고 주장하지 않는다.
- DB 재개방 후 `greet → calls → normalize_name` path 길이 1, 변경 엔티티 version 2, history versions `[2, 1]`을 확인했다.
- CLI entity query가 같은 version 2 엔티티를 반환했다.
- wiki rebuild가 entity 2개·source 1개·index의 **4개 파일**을 생성했다.
- wiki doctor: **broken links 0, lint errors 0, warnings 1**. 직접 만든 entity에 source metadata가 없어 fallback `graph://rebuild` source page가 `stale-candidate`로 보고되었다. 무경고 통과라고 기록하지 않는다.

### 7.2 ai-memory

빌드:

```text
cargo build --locked -p ai-memory-cli --bin ai-memory
```

dev binary 빌드 성공. 이어서 다음 실제 CLI/server 경로를 사용했다.

```text
ai-memory --data-dir <tmp>/ai-memory init
ai-memory --data-dir <tmp>/ai-memory serve --transport http --bind 127.0.0.1:49389 --no-watcher --workspace comparison --project smoke
AI_MEMORY_SERVER_URL=http://127.0.0.1:49389 ai-memory ... write-page --workspace comparison --project smoke --path decisions/storage.md --body <synthetic-body> --kind decision
ai-memory ... search MnemosyneComparisonToken --workspace comparison --project smoke --json
ai-memory ... read-page --path decisions/storage.md --workspace comparison --project smoke --json
```

관찰 결과:

- `write-page → HTTP server → wiki/SQLite → search/read-page` 왕복 성공. 검색이 정확한 `decisions/storage.md`를 반환했다.
- 실제 `/hook?event=...&agent=...&workspace=comparison&project=smoke&ingest_key=...`에 synthetic session-start/user-prompt/session-end를 전송했다. 일반 응답은 **HTTP 202, text `queued`**였다. 처음 smoke 클라이언트의 JSON 가정은 틀렸으며, 이후 text 응답으로 처리했다.
- 비동기 처리 후 `ComparisonLifecycleToken` 검색이 생성된 `sessions/<id>.md`를 반환했다. LLM 없이 session page가 생긴 것을 확인했다.
- `handoffs --json`에서 `from_agent: claude-code`인 열린 자동 handoff 1개를 관찰했다. 이후 Codex session-start에도 이 실험의 기본 요청 방식에서는 열려 있었다. **자동 주입·claim-once 경쟁·owner 격리는 실행 검증하지 않았다.**
- synthetic 문자열 `OPENAI_API_KEY=FAKE_ONLY_NOT_A_REAL_KEY`가 page readback에서 `[REDACTED:env_secret]`로 바뀌었다. 실제 credential은 사용하지 않았다.

### 7.3 검증 한계와 정리

- semantic extraction 모델, embedding 품질, LLM consolidation/dream, 전체 MCP protocol, 웹 UI, 인증·팀 운영, 실제 harness 설치/호환성, Onyx/Slack live 연결은 검증하지 않았다.
- 두 시스템의 검색 정확도·처리량·메모리 사용량 우열을 측정하지 않았다. README의 테스트 개수·성능 수치를 이번 결과로 인용하지 않았다.
- 임시 ai-memory 서비스를 종료하고 synthetic 임시 파일을 제거했다. 조사용 permanent test나 smoke script는 추가하지 않았다.
- ai-memory source build의 `target/` 산출물과 Rust/Cargo 도구·의존성 cache는 남는다. 애플리케이션 코드와 기존 사용자 데이터는 수정하지 않았다.

## 8. 주요 근거 위치

`M`은 현재 Mnemosyne 저장소, `A`는 옆의 ai-memory 저장소다. `A` 링크는 조사 당시처럼 두 checkout이 같은 부모 디렉터리에 있을 때 동작한다. 줄 번호는 조사 시점 기준이며, 이동 시 함께 적힌 symbol을 기준으로 찾는다.

### Mnemosyne

- **[M1]** [pyproject.toml](../pyproject.toml), [README](../README.md): 버전·의존성·제품 지향. README의 기능 소개와 실제 경로를 구분했다.
- **[M2]** [graph/knowledge_graph.py](../mnemosyne/graph/knowledge_graph.py): `KnowledgeGraph.__init__`(94–124), entities/relations/history, `add_entity`, `update_entity`, `query`, `get_entity_history`, tombstone/timeline API.
- **[M3]** [ingest/ingester.py](../mnemosyne/ingest/ingester.py): `_add_file`(194–260); [llm_extractor.py](../mnemosyne/ingest/llm_extractor.py): `extract_text`(64–108), `extract_file`(110–130); [llm_bridge.py](../mnemosyne/ingest/llm_bridge.py): provider/fallback(98–163); [extraction/cli.py](../mnemosyne/extraction/cli.py): coding dispatch(79–111); [pipeline.py](../mnemosyne/extraction/pipeline.py).
- **[M4]** [retrieval/engine.py](../mnemosyne/retrieval/engine.py): `query`/cache(220–328), strategy/placeholder(450–480), invalidation(573–585); [mcp/tools.py](../mnemosyne/mcp/tools.py): `_search`(169–189); [graph/fts.py](../mnemosyne/graph/fts.py).
- **[M5]** [graph/project.py](../mnemosyne/graph/project.py), [connection_pool.py](../mnemosyne/graph/connection_pool.py), [deterministic/code_parser.py](../mnemosyne/extraction/deterministic/code_parser.py): project identity, read pool, AST 추출.
- **[M6]** [wiki/llm_wiki.py](../mnemosyne/wiki/llm_wiki.py): `rebuild_from_graph`(681–736), generated block 보존·atomic write; [ingest/update.py](../mnemosyne/ingest/update.py): hash 기반 update.
- **[M7]** [AGENT_HANDOFF.ko.md](AGENT_HANDOFF.ko.md), [NEXT_WORK_ITEMS.ko.md](NEXT_WORK_ITEMS.ko.md): 원본/Vault/DB 경계와 운영 승인. 과거 문서의 버전·테스트 결과는 이번 버전/실행 결과로 사용하지 않았다.
- **[M8]** [ARCHITECTURE.md](../ARCHITECTURE.md): Design Phase(1–6), Proposed Architecture(49–110); [mnemosyne-core/src/lib.rs](../mnemosyne-core/src/lib.rs), [setup.py](../setup.py): optional native export/build.
- **[M9]** [facts/store.py](../mnemosyne/facts/store.py), [jobs/queue.py](../mnemosyne/jobs/queue.py): 독립 validity/queue API.
- **[M10]** [wiki/budget.py](../mnemosyne/wiki/budget.py): access frequency 미연결 설명(8–25), token 추정(38–62).
- **[M11]** [integrations/onyx/exporter.py](../mnemosyne/integrations/onyx/exporter.py): policy mapping 후 publish, tombstone suppression/withdrawal; [mapper.py](../mnemosyne/integrations/onyx/mapper.py).
- **[M12]** [integrations/slack/api.py](../mnemosyne/integrations/slack/api.py): live guard(97–139); [acl.py](../mnemosyne/integrations/slack/acl.py): channel·freshness deny(125–151); [graph/knowledge_graph.py](../mnemosyne/graph/knowledge_graph.py): `ISOLATED_SOURCE_CHANNELS`(17–26).
- **[M13]** [hooks/cli.py](../mnemosyne/hooks/cli.py), [mcp/server.py](../mnemosyne/mcp/server.py), [BINARY_INSTALL.md](BINARY_INSTALL.md): 통합·배포 표면.

### ai-memory

- **[A1]** [README](../../ai-memory/README.md), [Cargo.toml](../../ai-memory/Cargo.toml), [support-matrix](../../ai-memory/docs/support-matrix.md): 제품 목표·version·harness 지원 구분.
- **[A2]** [docs/ARCHITECTURE.md](../../ai-memory/docs/ARCHITECTURE.md): capture/compile/recall, 선택 기능·보존 정책. 문서 설명은 아래 구현과 교차 확인했다.
- **[A3]** [commands/search.rs](../../ai-memory/crates/ai-memory-cli/src/commands/search.rs): thin HTTP client(1–41); [hooks/synth.rs](../../ai-memory/crates/ai-memory-hooks/src/synth.rs): `synthesize_session_page`.
- **[A4]** [store/writer.rs](../../ai-memory/crates/ai-memory-store/src/writer.rs): bounded channel, 전용 writer thread, `Sanitized<NewObservation>` 입력, startup delivery transaction.
- **[A5]** [store/reader.rs](../../ai-memory/crates/ai-memory-store/src/reader.rs): hybrid RRF/explain/authority(4923–5403); [retrieval_tuning.rs](../../ai-memory/crates/ai-memory-store/src/retrieval_tuning.rs): opt-in tuning defaults.
- **[A6]** [commands/reindex.rs](../../ai-memory/crates/ai-memory-cli/src/commands/reindex.rs): 복구 제외 state(16–18, 47–63), 빈 DB 요구; [mcp/admin.rs](../../ai-memory/crates/ai-memory-mcp/src/admin.rs): online backup(785–867).
- **[A7]** [wiki/wiki.rs](../../ai-memory/crates/ai-memory-wiki/src/wiki.rs): `write_page` 정제·admission·file/DB update와 rollback(2094–2280), `reindex_all`.
- **[A8]** [core/sanitize.rs](../../ai-memory/crates/ai-memory-core/src/sanitize.rs): pattern/control strip, `Sanitized<NewObservation>`(327–353), UTF-8 head/tail cap; [hooks/capture_policy.rs](../../ai-memory/crates/ai-memory-hooks/src/capture_policy.rs).
- **[A9]** [store/ops.rs](../../ai-memory/crates/ai-memory-store/src/ops.rs): session-end/handoff transaction·`accept_handoff_in_transaction`(2794–3103); [hooks/payload.rs](../../ai-memory/crates/ai-memory-hooks/src/payload.rs): HTTP query contract(22–92), event vocabulary(332–390).
- **[A10]** [store/decay.rs](../../ai-memory/crates/ai-memory-store/src/decay.rs), [consolidate/sweep.rs](../../ai-memory/crates/ai-memory-consolidate/src/sweep.rs), [dream.rs](../../ai-memory/crates/ai-memory-consolidate/src/dream.rs): 강화·TTL/삭제·opt-in rewrite.
- **[A11]** [evals/README.md](../../ai-memory/evals/README.md), [retrieval/score.rs](../../ai-memory/evals/src/retrieval/score.rs): session 중복 제거와 hit@k/recall@k(1–94).
- **[A12]** [hooks/router.rs](../../ai-memory/crates/ai-memory-hooks/src/router.rs): opt-in brief·compose-before-claim(1191–1420), budget renderer(1552–1583, 1713–1815).
- **[A13]** [store/ops.rs](../../ai-memory/crates/ai-memory-store/src/ops.rs): hash/canonical metadata·supersession·evidence(1044–1160); [workstream/lib.rs](../../ai-memory/crates/ai-memory-workstream/src/lib.rs), [store/workstream.rs](../../ai-memory/crates/ai-memory-store/src/workstream.rs): managed runtime 범위.
- **[A14]** [LICENSE](../../ai-memory/LICENSE): MIT 고지 보존 조건.
