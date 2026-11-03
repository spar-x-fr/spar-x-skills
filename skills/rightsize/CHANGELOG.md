# Changelog

All notable changes are listed here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

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
