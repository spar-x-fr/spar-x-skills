---
name: "rightsize"
description: "Elite work strategy for every non-trivial task: quality first, then the right plan, model, effort, mode and scoped verification. Use before multi-step work, delegating, running tests, or cost/token questions."
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

## 1. Think once, at the right level

Before acting on non-trivial work, pick the playbook for the work type in the
**Expert playbooks** appendix below (bug, feature, refactor, research, review,
migration, performance, docs). Each one gives the expert sequence, where the hard
thinking goes, what to delegate and how to verify. Hard thinking happens once, up
front, on the strongest model the task needs; execution then runs on cheaper tiers
against that plan.

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

| Situation | Model | Effort |
|---|---|---|
| T0 | no model: run the tool | — |
| READ, or BULK with an exact spec and a check, R ≤ 1 | haiku | low |
| peak ≤ 1 | haiku, or sonnet if others build on the result | low |
| peak = 2 | sonnet | medium |
| peak = 3 only through the risk bonus | opus | medium |
| peak = 3 because C or A = 3 | opus plans (high), sonnet executes (medium) | |
| peak = 3 because D = 3, or R = 3 | opus | high |
| D = 3 and R ≥ 2, or long autonomous run | opus | xhigh |
| opus xhigh failed on it | fable, or opus max | xhigh / max |

**Effort, measured.** 100 headless runs in October 2026: 4 tasks with hidden tests or
an oracle (bug fix, 6 subtle bugs, a constrained routing algorithm, a regex engine
checked against Python's `re`), Haiku, Sonnet and Opus 5.5. Every run passed from
`low`. Above `medium` nothing improved: `xhigh` cost 1.4–2.2× `high`, `max` 3.7–9.3×,
with 4–7× the wall time. So:

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

Optional agents shipped with the rightsize plugin (only if installed): `rs-scout`
(haiku/low), `rs-verifier` (haiku/low), `rs-builder` (sonnet/medium), `rs-sage`
(opus/high).

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

- During work, run only what the change touches: `python scripts/test_scope.py --run`
  (script shipped with the rightsize plugin; without it, run the tests that cover the
  changed files). It picks the tests mapped to changed files and falls back to the
  full suite when a shared file changed, the impact is unknown, or the last full run
  is red or stale.
- At the end of a sprint, before a commit that closes work, or before a release:
  `test_scope.py --full --run`. The result is recorded in
  `.claude/rightsize/test-ledger.json`; say in the final report when the last full
  green run was.
- Delegate long test runs to `rs-verifier` so their output stays out of the main
  context.

## 7. Escalate and de-escalate on evidence

Escalate one rung, effort before model, when: the same check fails twice, output
contradicts the code or a test, a reviewer finds a high-severity defect, or a report
is low confidence. Main thread: `ultrathink` for one turn rather than flipping
`/effort`; send the hard part to an opus sub-agent rather than `/model`, which forces
a full cache re-write.

De-escalate when a plan is approved (execute on sonnet/haiku) or after two easy turns
at high effort. Never on security, money, migrations, deletion or anything published.

## 8. Protect the cache and the context

- Do not change the main model mid-session: caches are per model, and Opus 5.5 and
  Sonnet 5.5 cache reads cost the same.
- Do not edit CLAUDE.md, rules or settings mid-session.
- Before a pause over an hour, finish the step or leave a hand-over note.
- `/compact` at a natural boundary with a focus line.

Details and cost arithmetic: the **Rightsize reference** appendix below. The plugin
also ships `scripts/token_audit.py` (real spend) and `scripts/agent_audit.py` (agents
without `model`/`effort`).

---

# Appendix A — Expert playbooks

One per work type. Each says where the hard thinking goes, what can be delegated
cheaply, and how the result is proved. Model/effort are starting points from the
routing table; raise them when the score says so. Quality bar first, always.

## Bug fix

1. **Reproduce first** (inline or rs-builder, sonnet/medium): a failing test or a
   command that shows the bug. No fix without a reproduction, unless reproduction is
   impossible and you say so.
2. **Locate** (rs-scout, haiku/low): where the failing path runs, recent changes to it
   (`git log -L`, `git blame`), similar code.
3. **Find the root cause** (sonnet/medium; opus/high if D = 3 or two hypotheses died):
   explain why the bug happens, not only where. Check whether the same cause hits
   other call sites.
4. **Fix at the cause**, smallest change that removes it. Keep the reproduction as a
   regression test.
5. **Verify**: `test_scope.py --run`; the reproduction passes, nothing near it breaks.
Smells of a shallow fix: a guard added at the symptom, a retry, a broadened `except`.

## Feature

1. **Shape** (opus/high when A ≥ 2, else sonnet/medium): restate the goal, the
   acceptance criteria, the edge cases and what is out of scope. Ask the user only what
   the code cannot answer.
2. **Survey** (rs-scout): existing patterns, the module that owns this concern,
   helpers to reuse. Match them.
3. **Plan the slices** so each one is shippable and testable on its own; order them
   along the dependency path.
4. **Build each slice** (rs-builder, sonnet/medium) test-first where the project tests.
5. **Verify each slice** with `test_scope.py --run`; at the end of the feature
   `--full --run`.
6. **Review** (rs-sage, opus/high) only when R ≥ 2 or the feature touches auth, money,
   data or concurrency.

## Refactor

1. **Pin behaviour first**: tests that cover the code to move; add characterization
   tests where coverage is thin.
2. **Mechanical steps** (renames, moves, signature changes): a tool or codemod if one
   exists (T0), else haiku/low with an exact spec.
3. **Structural decisions** (new boundaries, abstractions): opus/high, once, written
   down before any edit.
4. **Small commits of pure refactor**: never mix behaviour changes in.
5. **Verify** after each step with `test_scope.py --run`; full suite at the end.

## Research and lookup

1. Ask the narrowest question that settles the decision.
2. rs-scout (haiku/low) for code and docs; one sub-agent per independent source, not
   per page.
3. Cross-check any claim that will drive a decision in a second source or in the
   code itself.
4. Deliver: answer, evidence with links or `file:line`, confidence, what is unknown.

## Code review

1. Read the diff and the intent (PR text, ticket) first; review against intent.
2. Mechanical checks by tools (lint, types, tests via `test_scope.py`), not by a model.
3. Reasoning review on sonnet/high; opus/high for security, concurrency, money, data
   migrations.
4. Report only defects you can explain with a concrete failure scenario, ranked by
   severity. Style nits last or not at all.

## Migration, data or infrastructure change (R = 3)

1. **Plan first** on opus/high: current state, target, step order, rollback for each
   step, what is irreversible, how to verify each step.
2. Dry-run or rehearse on a copy when possible.
3. Execute step by step on sonnet/medium, verifying before the next step.
4. Full test suite and an explicit check of the irreversible parts before declaring
   done. Ask the user before any irreversible or outward-facing step.

## Performance

1. **Measure before touching anything**: a benchmark or profile that shows where the
   time goes. No optimisation without a number.
2. Hypothesis and fix on sonnet/medium; opus/high for algorithmic or concurrency work.
3. Measure again with the same benchmark; report before/after with the method.
4. Keep the fix only if the gain is real and the tests stay green.

## Documentation

1. Facts from the code, not from memory: rs-scout gathers them with `file:line`.
2. Writing on sonnet/medium; haiku/low for mechanical updates (renamed flags, paths).
3. Run every command and example you publish.

## Sprint close

1. `test_scope.py --full --run` and record the result in the ledger.
2. Re-run anything flagged `unmapped` during the sprint and add the missing tests.
3. Write what was learned (decisions, traps, measured numbers) to memory or the
   project's docs, not to chat only.

---

# Appendix B — Rightsize reference

Loaded only when the sections above are not enough. Prices and mechanisms checked on
2026-10-27 against platform.claude.com and code.claude.com; re-check before
quoting dollars.

## The arithmetic behind the rules

| Model | Input $/MTok | Output $/MTok | Cache read | 1-hour cache write |
|---|---|---|---|---|
| Fable 5.1 | 10 | 50 | 0.25 | 20 |
| Opus 5.5 | 4 | 20 | 0.20 | 8 |
| Sonnet 5.5 | 2 | 10 | 0.20 | 4 |
| Haiku 5.5 | 0.10 (0.50 above 100k) | 0.50 (2.50 above 100k) | 0.01 | 0.20 |

What follows from it:

1. **Haiku is the big lever, Sonnet a modest one.** Haiku costs 1/40 of Opus on
   input and output. Sonnet costs half of Opus, and the same on cache reads.
2. **In a long session most input is cache reads** (97% on the author's own month of
   usage). On Opus and Sonnet those cost the same, so moving a cached session from
   Opus to Sonnet only saves on output, and pays a full cache re-write.
3. **Output is where effort bites.** Effort mostly changes how much the model thinks
   and how many tool calls it makes. Output costs 5x input, so a lower effort on the
   same model is often the cheapest saving that keeps quality.
4. **A sub-agent has a start-up cost.** Its first request writes its own cache: the
   system prompt plus tool definitions, about 15k to 30k tokens. That is about
   USD 0.12 to 0.24 on Opus with a one-hour write, under USD 0.01 on Haiku. Delegating a
   two-call lookup to an Opus sub-agent costs more than doing it inline; delegating
   it to Haiku costs almost nothing.
5. **Caches are per model.** A cascade that tries Haiku, then Sonnet, then Opus on
   the same context pays three cache writes. Send the cheap model a narrow brief
   instead of the whole conversation.

## What Claude Code really lets you control

| Lever | Where | Notes |
|---|---|---|
| Sub-agent model | `model:` in `.claude/agents/*.md`, or `model` on the Agent call | the call wins over the frontmatter |
| Sub-agent effort | `effort:` in the agent file, or `effort` on the Agent call | without it the agent inherits the session effort |
| Skill or command model / effort | `model:` / `effort:` in SKILL.md or commands/*.md | applies while the skill runs; with `context: fork` it sets the forked agent |
| Session model | `/model`, `--model`, `model` in settings | `opusplan` = Opus in plan mode, Sonnet to execute |
| Session effort | `/effort`, `--effort`, `effortLevel` in settings, `CLAUDE_CODE_EFFORT_LEVEL` | `ultrathink` raises one turn only |
| Hooks | `UserPromptSubmit` can add context; `PreToolUse` can rewrite tool input | no hook can change the main session's model or effort |

Because no hook can change the main model, a prompt classifier in a hook can only
print advice, and that advice is paid for on every prompt. This skill does not ship
one. The routing happens where it can act: the Agent call and the agent files.

## Worked examples

| Request | Scores | Route |
|---|---|---|
| "Where is the retry backoff defined?" | READ, R0 | rs-scout or Explore, haiku/low |
| "Run prettier on src/" | T0 | run the formatter, no model |
| "Rename `calc` to `compute_area` everywhere, add type hints" | C1 R1 A0 D1 | haiku/low inline if a few files, else a haiku sub-agent |
| "Fix the failing duration-parser tests" | C1 R1 A1 D2 | sonnet/medium |
| "Add pagination to the orders API, with tests" | C2 R1 A1 D2 | sonnet/medium sub-agent, opus reviews only if the diff touches auth |
| "Migrate the users table to a new schema in prod" | C2 R3 A1 D2 | plan with opus/high, execute steps on sonnet, opus reviews the migration |
| "Requests hang once a day, no idea why" | C2 R2 A2 D3 | opus/xhigh, read-only investigation first |
| "Implement an optimal scheduler with precedence constraints" | C1 R1 A0 D3 | opus/high |
| "Translate these 200 product descriptions" | BULK, R1 | haiku/low, batched |
| Same task failed twice on sonnet/medium | +2 failures | sonnet/high, then opus/high |

## Briefing a cheaper model

Cheaper models fail more often on vague briefs than on hard ones. A good brief:

- names the goal in one sentence and the files or URLs to start from;
- says what done looks like and how to check it (the test command, the expected
  shape of the answer);
- caps the answer length and asks for `file:line` evidence;
- says what not to touch.

If you cannot write that brief, the task is not ready for a cheaper model: plan it
first.

## What was rejected, and why

From a code review of ruvnet/ruflo (commit 9e65711, October 2026):

- **Keyword classifiers on the prompt.** Its router scores English keywords by
  substring (`add` matches `address`) and its hook prints a recommendation box on
  every prompt without changing the model. The model reading this skill understands
  the request better than any keyword table.
- **Huge always-loaded instructions.** A 73 KB CLAUDE.md is read on every request.
  This skill keeps the core short and the reference at the end.
- **Unmeasured multipliers.** Every number here comes from the pricing page or from
  `bench/` runs you can repeat.

Kept from it: scoring several dimensions instead of one "difficulty", escalating on
observed failure, and sending deterministic edits to a tool instead of a model.

---

Source: github.com/Ayoubhm07/rightsize (MIT licence, © 2026 Ayoub), skill
`skills/rightsize`, with PLAYBOOKS.md and ROUTING.md as appendices.