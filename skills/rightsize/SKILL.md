---
name: rightsize
description: Elite work strategy for every non-trivial task - quality first, then the smartest plan, model (Haiku/Sonnet/Opus/Fable), effort (low→max), mode (inline, sub-agent, plan, session) and scoped verification. Use before multi-step work, before delegating to a sub-agent, before running tests, and when the user asks about cost, tokens, model or effort.
---

# Rightsize: elite quality, spent wisely

## Rule 0: quality before optimisation

The deliverable must reach the standard of the best expert in the field: correct,
verified, root causes found, nothing a senior reviewer would send back. Savings never
come from weaker reasoning on the deliverable. They come from everything around it:
no work done twice, no useless parallelism, no full test run for a one-line change,
cheap models for lookups and mechanical steps.

When two tiers both look possible for the deliverable, take the stronger one. When a
step is a lookup, a mechanical edit or a test run, take the cheapest one that is
verified by a check.

Never stop at the first plausible answer. Verify it against the code, a run or a
source; look for the case that breaks it; then deliver.

**Trivial work skips the rest.** A direct answer, a lookup or a one-step edit with an
obvious check gets no scoring and no playbook: do it, verify it, deliver. The method
below must cost less than the waste it prevents.

## 1. Think once, at the right level

Before acting on non-trivial work, pick the playbook for the work type in
[PLAYBOOKS.md](PLAYBOOKS.md) (bug, feature, refactor, research, review, migration,
performance, docs; and outside code: writing, data and documents, actions taken in
someone's name, unattended runs). Each one gives the expert sequence, where the hard thinking goes,
what to delegate and how to verify. Hard thinking happens once, up front, on the
strongest model the task needs; execution then runs on cheaper tiers against that
plan.

Decompose by dependency, not by count: find the critical path, keep it sequential and
in one head; parallelise only steps that are independent and each worth a sub-agent.
Two or three well-briefed agents beat ten vague ones.

## 2. Score the task (0 to 3 each, silently)

| Axis | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **C** scope | 1 file, 1 step | few files, clear | many files or steps | cross-cutting, architecture |
| **R** risk | throwaway | normal code with tests | prod, data, public text | security, money, migrations, deletion |
| **A** ambiguity | exact spec | small gaps | design choices open | goal unclear |
| **D** depth | lookup, copy | standard logic | non-obvious bug or design | novel algorithm, concurrency, unknown cause |

Flags: **T0** a deterministic tool can do it · **READ** read-only · **BULK** same step
over many items · **CTX** needs this conversation · **CHK** tests, an oracle or a
compiler will prove the result.

## 3. Map the score

`peak = max(C, A, D)`, plus 1 if `R ≥ 2` (cap 3).

Read the table top to bottom and stop at the first row that matches (the order
`scripts/route.py` applies):

| Situation | Model | Effort |
|---|---|---|
| T0 | no model: run the tool | — |
| READ, or BULK with an exact spec and a check, R ≤ 1 | haiku | low |
| peak ≤ 1 | haiku, or sonnet if others build on the result | low |
| peak = 2 | sonnet | medium |
| D = 3 with R ≥ 2, or D = 3 in a long autonomous run | opus | xhigh |
| D = 3, or R = 3 | opus | high |
| C or A = 3 | opus plans (high), sonnet executes (medium) | |
| peak = 3 only through the risk bonus | opus | medium |

After a failure at opus xhigh: fable at xhigh, then fable at max (section 7).

**Effort, measured.** 100 headless runs in October 2026: 4 tasks with hidden tests or
an oracle (bug fix, 6 subtle bugs, a constrained routing algorithm, a regex engine
checked against Python's `re`), Haiku, Sonnet and Opus 5.5. Every run passed from
`low`. Above `medium` nothing improved: `xhigh` cost 1.4–2.2× `high`, `max` 3.7–9.3×
and up to 11× the wall time. So:

- **CHK**: start one effort level below the table (never when R = 3). The check, not
  the effort, guarantees the quality; a failure climbs the ladder.
- **No check** (design, review, ambiguous or long autonomous work): keep the table.
  That is where effort buys quality, and where Rule 0 says to take the higher tier.
- `max` only after `xhigh` failed. `ultracode` is not an effort level but a
  multi-agent workflow mode: only when the user asks for it.

## 4. Pick the mode

- **Inline**: needs CTX, or under about 3 tool calls.
- **Sub-agent**, with `model` and `effort` set on the Agent call: heavy reading the
  main thread does not need, a cheaper tier, or an independent piece. Built-in agents
  inherit the session effort otherwise: `Explore` → haiku/low.
- **Plan first** (plan mode or `opusplan`): C ≥ 2 and A ≥ 2, or any R = 3 change.
- **Separate session**: an independent deliverable, or context past about 60%.
- **Multi-agent workflow**: only when the user asks.

Optional agents shipped with this skill: `rs-scout` (haiku/low), `rs-verifier`
(haiku/low), `rs-builder` (sonnet/medium), `rs-sage` (opus/high).

## 5. Agent-to-agent protocol

Brief (main → sub-agent), under 300 words:
`GOAL` one sentence · `CONTEXT` files, facts already known, what was ruled out ·
`DONE WHEN` the check that proves it · `LIMITS` what not to touch, answer length.

Report (sub-agent → main):
`STATUS` done / partial / blocked · `RESULT` · `EVIDENCE` file:line, commands and
output · `CONFIDENCE` high / medium / low and why · `NEXT` what is left.

Treat a report as a claim: check the evidence before building on it. A low-confidence
or unverified report escalates (section 7), it is never passed on as fact.

## 6. Verify smart, not everything every time

Verification is what lets effort stay low without risking quality: before
starting, write or locate the check that will prove the result.

- During work, run only what the change touches:
  `python scripts/test_scope.py --run` (paths are relative to this skill's folder; the session rules give the absolute path).
  It picks the tests mapped to changed files and falls back to the full suite when a
  shared file changed, the impact is unknown, or the last full run is red or stale.
- At the end of a sprint, before a commit that closes work, or before a release:
  `test_scope.py --full --run`. The result is recorded in
  `.claude/rightsize/test-ledger.json`; say in the final report when the last full
  green run was.
- Delegate long test runs to `rs-verifier` so their output stays out of the main
  context.
- No test suite (text, data, documents, actions)? The check still exists and is named
  before starting: a source for every fact, figures recomputed, the file opened and
  looked at, a dry run before anything is sent. Each playbook names its check.

## 7. Escalate and de-escalate on evidence

Escalate one rung, effort before model, when: the same check fails twice, output
contradicts the code or a test, a reviewer finds a high-severity defect, or a report
is low confidence. Main thread: `ultrathink` for one turn rather than flipping
`/effort`; send the hard part to an opus sub-agent rather than `/model`, which forces
a full cache re-write.

De-escalate when a plan is approved (execute on sonnet/haiku) or after two easy turns
at high effort. Never on security, money, migrations, deletion or anything published.

## 8. Protect the cache and the context

- Do not change the main model mid-session: caches are per model, so the switch
  pays a full cache re-write.
- Do not edit CLAUDE.md, rules or settings mid-session.
- Before a pause over an hour, finish the step or leave a hand-over note.
- `/compact` at a natural boundary with a focus line.

## 9. When the levers are missing

Chat apps, a single-model API call or a harness without `model`/`effort` on the Agent
call cannot route. Everything else still applies: Rule 0, the playbook, the check
named before starting, the brief and report formats, escalation on evidence. The
score then decides how much to plan, whether a sub-agent is worth its start-up cost
and how much to verify, not which model runs. Never claim a routing, a script run or
a saving that did not happen in this session.

Details and cost arithmetic: [ROUTING.md](ROUTING.md). Measure real spend:
`scripts/token_audit.py`. Agents without `model`/`effort`: `scripts/agent_audit.py`.
