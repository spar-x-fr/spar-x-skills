# Maintainer notes

## Repository settings already applied

- Squash merges only, branches deleted after merge, no wiki or projects.
- Workflow token read-only by default; workflows cannot approve pull requests.
- Actions restricted to GitHub-owned actions plus an allowlist
  (`step-security/harden-runner`, `ossf/scorecard-action`, `trufflesecurity/trufflehog`),
  and every action must be pinned to a full commit SHA.
- Dependabot alerts and automated security fixes on; Dependabot version updates for
  GitHub Actions and the pinned development tools.

## When the repository goes public

Some protections are unavailable on a private repository without a paid plan. Turn
them on right after making it public:

```bash
gh repo edit Ayoubhm07/rightsize --visibility public --accept-visibility-change-consequences

# Branch protection, kept as code in .github/rulesets/
gh api -X POST repos/Ayoubhm07/rightsize/rulesets --input .github/rulesets/protect-main.json

# GitHub secret scanning with push protection
gh api -X PATCH repos/Ayoubhm07/rightsize --input - <<'JSON'
{"security_and_analysis": {"secret_scanning": {"status": "enabled"},
                           "secret_scanning_push_protection": {"status": "enabled"}}}
JSON

# Private vulnerability reporting (used by SECURITY.md)
gh api -X PUT repos/Ayoubhm07/rightsize/private-vulnerability-reporting
```

CodeQL and OpenSSF Scorecard start on their own: their jobs are skipped only while the
repository is private.

## Releasing

1. Update `CHANGELOG.md` and the version in `.claude-plugin/plugin.json`,
   `.claude-plugin/marketplace.json` and `pyproject.toml`.
2. Merge through a pull request with all checks green.
3. `claude plugin tag .` creates the `rightsize--v<version>` tag; push it.

## Refreshing pins

Dependabot proposes updates for actions and tools. When updating
`requirements-dev.txt` by hand, take every hash from the PyPI JSON API and check the
install with `pip install --require-hashes --no-deps -r requirements-dev.txt`.
