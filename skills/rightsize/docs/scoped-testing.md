# Scoped testing

`scripts/test_scope.py` runs the tests a change can affect, and the
whole suite when that is the only safe answer. **When in doubt it runs more, never
less**: a missed regression costs more than a few seconds of tests.

## Commands

```bash
python test_scope.py                 # the plan, as JSON: mode, reason, tests, command
python test_scope.py --run           # run the plan and record the result
python test_scope.py --full --run    # the whole suite: sprint end, release, final commit
python test_scope.py --status        # the ledger: last full run and recent runs
python test_scope.py --run --cmd "pytest -q {tests}"   # your own runner
```

Run it from anywhere inside a git repository.

## Decision rules, in order

1. `--full`, no recorded green full run, a red last full run, or a stale one (7 days
   or 30 commits) → **full suite**.
2. A shared file changed: lockfiles, manifests (`package.json`, `pyproject.toml`,
   `pom.xml`, `*.csproj`...), test configuration (`conftest.py`, `jest.config.*`), CI
   workflows, `Makefile`, `Dockerfile` → **full suite**.
3. A changed file of a type it cannot map (`.yaml`, `.sql`, templates, fixtures...)
   → **full suite**.
4. A changed source file or test helper with no test mapped to it, even through its
   folder → **full suite**.
5. Otherwise → **scoped**: changed test files, plus tests named after a changed file
   or importing it (word-bounded, so `user` does not match `username`). Renamed and
   deleted files keep their old name, so the tests of the old module still run.
6. Only documentation or images changed → **nothing to run**.

Changes are measured against the commit of the last green full run, including
uncommitted and untracked files.

## The ledger

`.claude/rightsize/test-ledger.json` in your repository keeps the last full run and
the last 20 runs (date, commit, mode, result, duration, test count, command). A scoped
run never replaces the last full run. Commit the ledger if your team wants a shared
record, or add `.claude/rightsize/` to `.gitignore` to keep it local.

## Runners

Detected automatically: pytest (when configured), unittest, vitest, jest, `go test`
and `cargo test`. When tests in several languages are selected, the script refuses to
guess and asks for `--cmd`: running only the Python half while recording the whole
plan as green would be a lie. An empty full suite is refused for the same reason.

## Measured effect

On a 40-module repository after a one-module change: **11.4 s for the full suite,
0.7 s scoped**, with the right test selected.
