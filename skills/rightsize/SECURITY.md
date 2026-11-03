# Security policy

## Reporting a vulnerability

Report privately through **[GitHub security advisories](https://github.com/spar-x-fr/spar-x-skills/security/advisories/new)**.
Do not open a public issue. Include what you found, how to reproduce it and the
impact you expect. You will get an answer within 7 days.

## Scope

rightsize runs code on your machine in three ways, and all three are in scope:

- **Hooks** (`hooks/inject.py`) run at every session start and before every sub-agent
  call. They must never block a session, never read or send user data, and never
  modify the tool input beyond appending text to a sub-agent prompt.
- **Scripts** (`scripts/`) read local transcripts, git state and
  agent files. `agent_audit.py --apply` is the only one that writes files outside its
  own ledger, and it keeps a `.bak` copy first.
- **The benchmark** (`bench/`) starts Claude Code headless, which spends tokens on the
  account it is logged in with.

## How the project protects itself

- No runtime dependencies: the standard library only.
- CI actions pinned by full commit SHA; development tools pinned by version and hash.
- Least-privilege workflow permissions (`permissions: {}` by default), no persisted
  checkout credentials, workflows audited by zizmor.
- Secret scanning of the full history on every push and pull request; CodeQL and
  OpenSSF Scorecard once the repository is public.
