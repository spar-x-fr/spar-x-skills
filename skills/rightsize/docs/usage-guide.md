# Usage guide

## What happens on its own

With the plugin installed you do not need to type anything special.

| When | What rightsize does |
|---|---|
| A session starts | The rules are added once (about 200 tokens, then cached): rule 0, playbooks, scoped tests, agent protocol |
| Claude delegates to a sub-agent | The sub-agent rules are appended to its brief (about 130 tokens): quality bar, stay in scope, report format, scoped tests |
| Before non-trivial work | Claude loads the skill, picks the playbook for the work type and routes each step |
| After code changes | Tests run only where the change reaches; the full suite runs at the end of a sprint |

## Rule 0

**Quality before optimisation.** The deliverable must reach expert quality. Savings
come only from what does not touch it: lookups and mechanical steps on cheap models,
scoped tests, no useless parallelism, a stable prompt cache. When two tiers both look
possible for the deliverable itself, rightsize takes the stronger one.

## Talking to it

You can steer it in plain words:

| You say | Effect |
|---|---|
| "Plan this first" | Plan mode or `opusplan` before any edit |
| "Have code-reviewer check this at xhigh" | That one sub-agent call runs at `xhigh`, whatever its file says |
| "Search the repo for X with a cheap agent" | A Haiku `rs-scout` or `Explore` call |
| "This is the end of the sprint" | Full test suite, recorded in the ledger, plus the sprint-close playbook |
| "ultrathink" in your message | One turn at higher effort, without changing the session setting |
| "Which model and effort would you use for this?" | The skill explains its scoring for that task |

## Effort: the button and the agents

The effort button at the bottom of the app (or `/effort`) sets the effort of **your
conversation** and of built-in agents with no effort of their own.

Agents whose file contains `effort:` keep that level, whatever the button says. That
is deliberate: a search agent should not think at `xhigh` because your conversation
does. To change one agent:

- once: say it in your message ("run tdd-guide at high");
- for good: edit the `effort:` line in its file, or ask Claude to;
- everything at once: the `CLAUDE_CODE_EFFORT_LEVEL` environment variable overrides
  both the session and the agent files.

Which level for what is in [Effort and models](effort-and-models.md).

## Escalation

rightsize starts at the level the task needs and climbs only on evidence: the same
check failing twice, output that contradicts the code or a test, a reviewer finding a
high-severity defect, or a sub-agent reporting low confidence. One rung at a time,
effort before model:

```text
haiku low → haiku medium → haiku high → sonnet low → sonnet medium → sonnet high
→ opus medium → opus high → opus xhigh → fable xhigh → fable max
```

It never steps down on security, money, migrations, deletion or anything published.

## Playbooks

[`PLAYBOOKS.md`](../PLAYBOOKS.md) holds the expert
sequence for each work type: bug, feature, refactor, research, review, migration,
performance, documentation, sprint close. Each says where the hard thinking goes,
what is delegated cheaply and how the result is proved.

## Scoped tests

See [Scoped testing](scoped-testing.md). In short:

```bash
python <rightsize>/scripts/test_scope.py --run          # during work
python <rightsize>/scripts/test_scope.py --full --run   # sprint end
```

## Measuring your own savings

```bash
python <rightsize>/scripts/token_audit.py --since 2026-10-01 --until 2026-11-01
python <rightsize>/scripts/token_audit.py --since 2026-11-01
```

Compare the two reports: total, share per model, per effort, main thread against
sub-agents. Details in [Measuring](measuring.md).
