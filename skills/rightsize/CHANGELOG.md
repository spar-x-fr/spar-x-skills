# Changelog

All notable changes are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Playbooks outside code: writing and published content, data analysis and documents,
  actions taken in someone's name, scheduled or unattended runs.
- Fable 5.2 prices ($8 / $40 per MTok); the `fable` alias now points to it.
- Fast path for trivial work, a verification rule for work without a test suite, and
  a section for harnesses that cannot set `model` or `effort`.

### Fixed

- The routing table in `SKILL.md` now reads top to bottom in the order `route.py`
  applies: D = 3 and R = 3 rows come before the "opus plans, sonnet executes" row, the
  `xhigh` row no longer reads as "any long run", and the last rung matches the ladder
  (fable at xhigh, then fable at max). No routing rule changed.
- Sonnet 5.5 cache reads cost $0.10 per MTok, not $0.20 (pricing page, and the costs
  recorded in `bench/results/` match it). The claim that Opus and Sonnet cache reads
  cost the same is removed; the rule against switching model mid-session stays, for
  the cache re-write.
- Worked example in `ROUTING.md`: two failures from sonnet/medium reach opus/medium.
- Wall time of `max` recomputed from `bench/results/2026-10-31-effort-sweep.jsonl`:
  1.1–10.9× `high` per task and model, not 4–7×.

## [0.1.0] - 2026-10-31

### Added

- `rightsize` skill: rule 0 (quality before optimisation), task scoring, model and
  effort routing table, modes, agent-to-agent protocol, escalation ladder, cache rules.
- Expert playbooks for bugs, features, refactors, research, reviews, migrations,
  performance, documentation and sprint close.
- `test_scope.py`: scoped testing with a ledger of full runs.
- `token_audit.py`, `agent_audit.py`, `route.py`.
- Agents `rs-scout`, `rs-verifier`, `rs-builder`, `rs-sage`.
- Hooks that apply the rules in every session and every sub-agent brief.
- Benchmark with 8 graded tasks and published results: a routing benchmark (19 runs)
  and an effort sweep (100 valid runs).
