# CALDEA-M1 완료 검증 기록

판정: **PASS — M1 패키지 DoD**, 2026-09-26 (Pacific/Auckland, NZST +1200).
검증자는 이번 구현 에이전트이며 독립 reviewer/외부 하네스의 운영 PASS를 주장하지 않는다.

## 완료 판정 체크리스트

- [x] 필수 8개 산출물 존재, 각각 실질 내용 100자 이상. 아래 문자 수는 UTF-8을 decode한 문자 기준.
- [x] 새 산출물의 상대 링크 전부 존재·앵커 검사 통과. 사용자 승인 D001에 따라 시딩 문서의 원본 저장소 상대 링크는 **원본 경로 기준 검증 대상**이며 58개 별도 통과.
- [x] `bash -n install.sh` exit 0.
- [x] `skills/milestone-loop/SKILL.md` YAML frontmatter 존재, name/description 검사와 PyYAML `safe_load` 통과.
- [x] 권위 문서와 기억 역할·구현 한계 대조 완료. 아래 일관성 확인표 참조.
- [x] `git diff --stat`과 핵심 파일 mtime을 수집. 최종 사용자 보고에 최종 HEAD 기준 결과를 포함한다.

| 산출물 | 문자 수 | mtime: stat -f '%Sm %N' (NZST) |
|---|---:|---|
| README.ko.md | 2862 | Sep 26 11:52:32 2026 |
| docs/00-research.md | 4756 | Sep 26 11:54:16 2026 |
| docs/ROADMAP.md | 2088 | Sep 26 11:54:16 2026 |
| docs/install.md | 8336 | Sep 26 11:56:04 2026 |
| docs/workflow.md | 6881 | Sep 26 11:57:44 2026 |
| templates/AGENTS.md | 4383 | Sep 26 11:58:50 2026 |
| skills/milestone-loop/SKILL.md | 7838 | Sep 26 12:00:42 2026 |
| install.sh | 6763 | Sep 26 12:02:04 2026 |

## 실행 증거

검사 시 구현 revision: `5f2a9d8`. 구현 시작 직전 부모는 `32b9a4e`, 최초 시딩은 `d5538a3`이다. 읽기 중 다른 작업에서 추가한 `32b9a4e`의 `docs/knowledge/KN-2026-09-26-codex-401-stale-key.md`는 이번 구현이 아니며 변경하지 않았다. 완료 보고의 구현 diff는 `32b9a4e..HEAD`로 집계한다.

```text
$ python3 scripts/verify.py --source-links
PASS: 필수 산출물 8개(각 100자 이상), 새 문서 상대 링크 26개, YAML frontmatter, Bash 구문, diff 공백, 시딩 4개 SHA-256
PASS: 시딩 원본 경로 기준 링크 58개, 로컬 필독 자료 9개 hash 일치

$ python3 scripts/test_install.py
Ran 14 tests in 1.341s
OK

$ bash -n install.sh
(exit 0, 출력 없음)

$ git diff d5538a3...HEAD --check
(exit 0, 출력 없음)

$ git diff --stat
(출력 없음: 구현 파일별 커밋 완료)
```

설치 검사는 임시 프로젝트와 `--skills-dir`로 격리했다. 실제 사용자 홈의 AGENTS/스킬/MCP/훅은 변경하지 않았다. 14개 시나리오는 새 설치, 기존 UTF-8/개행 없는 파일, 원본 백업·mode 보존, 재설치 bytes/mtime 불변, CRLF 마커 앞뒤 및 ai-memory 마커 보존, drift 검출/복구, 잘못된 마커 거부, 동명 사용자 스킬 보존, symlink 거부, agents/claude 공존, 잘못된 인자/없는 경로, 셸 특수문자 경로, 동시 잠금 거부, 디렉터리 충돌, 동명 스킬 폴더의 추가 파일 보존을 포함한다. 관련 경우는 하나의 테스트 메서드에서 묶어 수행했다.

`--check`가 누락/드리프트에서 1, 유효한 설치에서 0, 인자/마커/소유권 충돌에서 2를 반환하고 쓰지 않는 것을 확인했다. YAML은 표준 라이브러리 검사의 JSON-compatible scalar 검사 외에 설치된 PyYAML 6.0.3으로도 파싱했다. 패키지 자체 검사에 PyYAML 설치는 필요 없다.

## 권위 자료 일관성 확인

| 확인한 경계 | 산출물 반영과 판정 |
|---|---|
| ai-memory는 작업 연속성; Mnemosyne는 구조화 지식 | README·설치·workflow·템플릿·스킬 일치, PASS |
| page/session/handoff와 entity/relation/history 구분 | graph 대체·단순 단기/장기 저장 구분으로 축소하지 않음, PASS |
| add의 LLM/CLI fallback과 Tree-sitter extract 분리 | dry-run은 offline 보장 아님, extract 출력은 DB 저장 증거 아님, PASS |
| 페이지 Markdown 복구와 운영 DB 백업 분리 | wiki git만으로 sessions/handoffs 복구 주장 없음, PASS |
| handoff CAS 보장 범위 | end-to-end exactly-once로 과장하지 않음, PASS |
| 현행 Python 경로와 optional Rust/hybrid 모듈 | 전체 Rust 전환·일반 MCP hybrid 연결 완료 주장 없음, PASS |
| Slack/Onyx 격리와 원문/파생자료 경계 | 진행 발송과 수집 분리, 일반 graph/세션 자동 합류 금지, PASS |
| 사실·설계·이번 실행의 구분 | VERIFIED(문서 확인/실행)와 PROPOSAL, 과거 smoke 미재실행 구분, PASS |
| Codex 종료 문서의 버전 차이 | 최신 지원 설명과 브리프 finalize 의무 함께 유지, D002 기록, PASS |

## 검증 범위의 끝

실제 ai-memory/Mnemosyne 서버 설치·MCP 왕복·하네스 간 인계·provider 수집·GitHub PR 리뷰/병합·Slack 발송은 이번 M1에서 실행하지 않았다. 운영 방법론의 성공은 ROADMAP의 후속 환경별 gate에서 별도 증명해야 한다. 시딩 4개의 bytes는 SHA-256 및 최초 커밋과의 diff로 보존을 확인했다. 외부 체크아웃 코드는 수정하지 않았다.

재실행 명령은 `python3 scripts/verify.py --source-links`, `python3 scripts/test_install.py`, `git diff 32b9a4e..HEAD --check`다. 배포 환경에 원본 체크아웃이 없으면 `--source-links` 없는 패키지 검사를 사용하고 원본 검증은 별도 환경의 증거로 취급한다.
