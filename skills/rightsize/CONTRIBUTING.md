# Contributing

Rule 0 applies to the project itself: **quality before optimisation**. A change is
welcome when it makes the work better and can show it.

## Set up

```bash
git clone https://github.com/Ayoubhm07/rightsize.git && cd rightsize
python -m pip install --require-hashes --no-deps -r requirements-dev.txt   # Python 3.11+
```

## Before you open a pull request

```bash
ruff check . && ruff format --check . && mypy
python -m unittest discover -s tests
claude plugin validate .
```

CI runs the same checks on Linux, macOS and Windows with Python 3.9, 3.12 and 3.13.

## What a good change looks like

- **Routing, effort or model rules** come with numbers: a `bench/` task or a rerun of
  an existing one, graded by a checker you validated with a passing reference and a
  failing variant. Opinions alone do not change the table.
- **Hooks** stay tiny, never fail a session, and never add text on every prompt.
- **Scripts** stay standard library only, typed (mypy strict), and fail safe: when in
  doubt, do more checking, not less.
- **Docs** say what was measured and what was not.
- Commits follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `ci:`...).

## Code of conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
