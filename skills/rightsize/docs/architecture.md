# Architecture

## Layout

```text
SKILL.md                 the strategy Claude reads: rule 0, scoring, routing, protocol
PLAYBOOKS.md             expert sequences per work type (loaded on demand)
ROUTING.md               cost arithmetic and Claude Code levers (loaded on demand)
scripts/
  route.py               the routing table as a pure, tested function
  test_scope.py          scoped testing with a ledger of full runs
  token_audit.py         where tokens and dollars go, from local transcripts
  agent_audit.py         finds agents without model/effort, proposes and writes them
  prices.py              list prices, one place to update
agents/                  rs-scout, rs-verifier, rs-builder, rs-sage
hooks/
  hooks.json             SessionStart and PreToolUse(Agent), auto-loaded by the plugin
  inject.py              prints the rules; never fails a session
bench/                   tasks, graders, runner, published results
tests/                   unit and regression tests (standard library unittest)
docs/                    these guides
```

## How it acts

```text
session starts ──► SessionStart hook ──► rules in context (once, ~200 tokens, cached)
                                             │
user asks for work ──► Claude loads SKILL.md ┤──► playbook + scoring + routing
                                             │
Claude delegates ──► PreToolUse(Agent) hook ─┴──► sub-agent rules appended to the brief
                                                   (model/effort set on the call or the agent file)
code changed ──► test_scope.py ──► scoped or full run ──► ledger
```

## Design decisions

**No prompt classifier in a hook.** No Claude Code hook can change the main
session's model or effort. A classifier in `UserPromptSubmit` could only print advice,
and that advice would cost tokens on every prompt. rightsize acts where Claude Code
really lets it: the Agent call, agent files, plan mode, and the strategy itself.

**The model scores the task, code applies the table.** The model understands a
request far better than any keyword list; `route.py` makes the mapping from scores to
model, effort and mode deterministic and testable.

**Rules travel in the brief.** On Claude Code 2.1.308 a `SubagentStart` hook's
context did not reach the sub-agent. A `PreToolUse` hook on `Agent` appending to the
prompt did, verified in a sub-agent transcript.

**Short always-on context.** SKILL.md is the only long text and loads only when the
skill is used; PLAYBOOKS.md and ROUTING.md load only when needed. The hooks add
about 200 tokens per session and 130 per sub-agent.

**Fail safe everywhere.** The hook exits 0 on any error. `test_scope.py` falls back
to the full suite on any doubt. The benchmark refuses to record infrastructure errors
as model failures. `agent_audit.py --apply` keeps the original of every file.

**Standard library only.** Nothing to install, nothing to audit at runtime. The
development tools (ruff, mypy, zizmor) are pinned by hash in `requirements-dev.txt`.
