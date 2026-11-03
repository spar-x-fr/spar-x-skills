# Agents and the agent-to-agent protocol

## The four rightsize agents

| Agent | Model / effort | Job |
|---|---|---|
| `rs-scout` | haiku / low | read-only lookups in code and docs, answers with `file:line` facts |
| `rs-verifier` | haiku / low | runs `test_scope.py`, keeps long test output out of the main thread |
| `rs-builder` | sonnet / medium | implements a well-specified change and proves it with the project's checks |
| `rs-sage` | opus / high | the hard part only: unknown root causes, concurrency, architecture, risky reviews |

They are ordinary Claude Code agents in `agents/`. Claude can call them by name, and
so can you ("ask rs-sage why this deadlocks").

## The protocol

Every delegation uses the same two shapes, so nothing is lost between agents.

**Brief** (main thread → sub-agent), under 300 words:

```text
GOAL       one sentence
CONTEXT    files, facts already known, what was ruled out
DONE WHEN  the check that proves it (a test command, an expected answer shape)
LIMITS     what not to touch, answer length
```

**Report** (sub-agent → main thread):

```text
STATUS      done / partial / blocked
RESULT      the answer or the change
EVIDENCE    file:line, commands run and their output
CONFIDENCE  high / medium / low, and why
NEXT        what is left
```

The main thread treats a report as a claim and checks its evidence before building
on it. A low-confidence or unverified report escalates; it is never passed on as fact.

The PreToolUse hook appends the sub-agent rules, including the report format, to
every Agent brief, so this holds for your own agents too, not only the `rs-*` ones.

## Giving your existing agents an effort level

An agent without `effort:` in its file inherits the session effort. `agent_audit.py`
lists them and proposes a level from the agent's name and role:

```bash
python <rightsize>/scripts/agent_audit.py            # read only
python <rightsize>/scripts/agent_audit.py --apply    # write, with .bak copies
```

`--apply` only adds missing `model:` / `effort:` lines, keeps the file's line
endings, never replaces an existing `.bak`, and running it twice changes nothing.

The proposals are heuristics. Review them, and raise to `high` any agent whose work
touches money, legal text, security, data migrations or anything published, where no
test can grade the result.

## How an agent's effort is decided

1. `effort` passed on the Agent call (for example "run code-reviewer at xhigh");
2. otherwise the `effort:` line in the agent's file;
3. otherwise the session effort.

`CLAUDE_CODE_EFFORT_LEVEL` in the environment overrides all three.
