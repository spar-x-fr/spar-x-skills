# Effort and models: what to use when

Everything here is either measured in this repository (`bench/results/`) or taken
from Anthropic's documentation, and says which. Prices are list prices checked on
2026-10-27.

## Models

| Model | Input / output $ per MTok | Use it for |
|---|---|---|
| Haiku 5.5 | 0.10 / 0.50 | lookups, reading, mechanical edits, bulk work, anything a test or oracle will check |
| Sonnet 5.5 | 2 / 10 | standard implementation, fixes, refactors, tests |
| Opus 5.5 | 4 / 20 | planning, hard bugs, architecture, review of risky changes |
| Fable 5.1 | 10 / 50 | only after Opus at `xhigh` failed on the task |

Two consequences of the price sheet worth knowing:

- Haiku costs 1/40 of Opus. Sonnet costs half of Opus, and the **same** on cache reads
  ($0.20 per MTok), which is most of a long session's input. Switching a cached
  session from Opus to Sonnet saves little and re-writes the whole cache: route the
  work through sub-agents instead.
- A sub-agent's first request writes its own cache (15k to 30k tokens). On Opus that
  costs more than a couple of inline tool calls; on Haiku it costs almost nothing.

## Effort levels

| Level | What it changes | Measured cost vs `high` | Use it for |
|---|---|---|---|
| `low` | short reasoning, few tool calls, terse answers | 0.4–1.1× | lookups, mechanical work, any verified task as a first try |
| `medium` | balanced; default of Opus 5.5 and Haiku 5.5 on the API | 0.5–1.0× | standard work; verified hard work as a first try |
| `high` | deep reasoning | 1× | work no check can grade: design, review, ambiguous or high-stakes tasks |
| `xhigh` | very deep reasoning, more tool calls | 1.4–2.2× | a hard task that failed at `high`, or hard and risky long autonomous runs |
| `max` | no limit on reasoning | 3.7–9.3×, 4–7× slower | only after `xhigh` failed; never a default |

### What the sweep measured

100 valid headless runs, 3 per cell, October 2026, on four tasks graded by hidden
tests or an oracle: a parser bug fix, six subtle bugs in a weighted TTL LRU cache,
a routing algorithm with mandatory stops and a toll quota, and a regex engine
compared with Python's `re` on 3 000 random patterns.

- **Every valid run passed, from `low` up**, on Haiku, Sonnet and Opus 5.5.
- Haiku at `low` built a regex engine that matched `re` on all 3 000 cases, three
  times out of three, for $0.02.
- Above `medium`, effort bought nothing measurable on these tasks; it only raised
  cost, time and output tokens (`max`: about 9–10× the output tokens of `high`).

### The rule rightsize applies

- **A check will prove the result** (tests, an oracle, a compiler): start one level
  lower than the routing table and let a failure climb the ladder. The check, not the
  effort, guarantees the quality. Never on maximum-risk work.
- **No check can prove it** (design, review, open-ended or long autonomous work):
  keep the table, and lean higher. That is where effort buys quality.

### Limits of the evidence

The tasks were well specified and verifiable, which is where low effort is safest.
Nothing here measures open-ended work. Haiku was not measured on the routing task
and only partly on the regex task (the API credit ran out; those runs were excluded,
not counted as failures).

## Special modes

| Mode | What it is | When |
|---|---|---|
| `ultrathink` (in a message) | raises effort for one turn, the session setting is unchanged | one hard turn in an otherwise easy session |
| `opusplan` (`/model opusplan`) | Opus in plan mode, Sonnet to execute | planning-heavy work with mechanical execution |
| `ultracode` | not an effort level: standing multi-agent workflow orchestration | very large, decomposable jobs, only when you ask; it spends a lot of tokens |
| `/fast` | the same Opus model, faster output at a premium price | latency matters more than cost |
