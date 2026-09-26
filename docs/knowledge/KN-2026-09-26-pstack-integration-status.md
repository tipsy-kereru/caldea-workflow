# KN-2026-09-26 — PStack 통합 현황: 방법론은 내장, 실행 인프라는 Phase 4 defer

**상태:** VERIFIED (패키지 실제 파일 대조로 확인, 2026-09-26)
**목적:** "칼데아 워크플로우에 PStack이 포함됐는가"에 대한 후속 세션·워커용 판정 기록. 다음 마일스톤 진행 시 이 문서가 기준선.

# PStack이 무엇인가 (출처: references/source-lauren-tan-grokbot.md)

Lauren Tan(GrokBot)의 스킬 운영 프레임워크. 3요소: ① 에이전트 실패 모드 관찰 ② 이를 마크다운 스킬로 점진 코다이프 ③ 스킬 자체를 Eval로 평가(블라인드 서브에이전트 테스트 + 독립 judge, Eval Playbook). GStack(엔지니어링 관행 기반 플러그인)에서 영감.

# 패키지에 내장된 부분 (M1 완료 시점 VERIFIED)

1. **실패 관찰 → 스킬/강한 제약 승격 룰**: `skills/milestone-loop/SKILL.md` — "반복 리뷰 지적은 회귀 테스트/린트와 스킬 개선 후보로 남긴다". 약한 제약(스킬) → 강한 제약(CI) 승격 경로와 함께 정의.
2. **양방향 강등 운영**: `docs/ROADMAP.md` "승격·강등 운영" — 게이트 누락·잘못된 병합 발견 시 자동화를 직전 단계로 강등 + 회귀 fixture 추가. 실패 관찰이 권한을 되돌리는 역방향 운영까지 명세. 실패를 SKIP으로 바꿔 승격 금지.
3. **Eval Playbook 명세 (Phase 4)**: 진입조건 = 실행 로그·실패 분류·고정 fixture corpus·측정 예산 확보. 수행 = 실패 관찰→스킬/린트 개선→블라인드 실행→독립 judge. 종료판정 = corpus 필수 안전/상태 전이 위반 0, baseline 대비 성공률 비하락 없음, 사전 합의 p95 시간·토큰 상한 준수, 모델·버전·seed·judge 근거·실패 사례 기록.
4. **사전 설계된 Eval corpus (8 시나리오)**: 정상 진행, 저장 지연, 이전 round 메시지 재도착, 필수 테스트 실패, 오래된 기억, scope 혼동, 3라운드 상한, Slack 중복 발송. fixture와 정답 분리(블라인드) 원칙 명시.
5. **원론 보존**: `references/source-lauren-tan-grokbot.md` §2.3에 PStack 3요소 원문.

# 아직 없는 것 (의도된 defer — Phase 4 실행 인프라)

- Eval 실행기(judge 에이전트 러너, 블라인드 테스트 하네스), corpus 저장소/관리 도구, 측정 예산 계기
- SKILL.md 명시: "스킬 Eval은 정상/실패/지연/중복 fixture, 실행 예산, 독립 judge를 갖춘 후 별도 단계로 수행"
- defer 이유: 신뢰 곡선 — 게이트 기계화(Phase 1)가 실전 증명되기 전 Eval을 돌리면 약한 제약 환경의 지름길 생산 위험. 순서 고정: M1(완료) → M2(실전 설치) → Phase 1 게이트 기계화 → Phase 2 리뷰 자동화 → Phase 3 자동 병합 → Phase 4 PStack 실행 인프라.

# 다음 진행 시 참조 경로

- Phase 4 명세: `docs/ROADMAP.md` (단계 표 + 블라인드 평가 문단 + 승격·강등 운영)
- 승격 룰: `skills/milestone-loop/SKILL.md` (완료 단계 문단) — 유저 레벨 설치본: `~/.agents/skills/milestone-loop/SKILL.md`
- 원론: `references/source-lauren-tan-grokbot.md` §2.3, `references/strategy-milestone-loop.md`