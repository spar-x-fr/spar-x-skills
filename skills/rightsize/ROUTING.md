# Rightsize reference

Loaded only when SKILL.md is not enough. Prices and mechanisms checked on
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
   $0.12 to $0.24 on Opus with a one-hour write, under $0.01 on Haiku. Delegating a
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
  This skill keeps SKILL.md short and loads this file only on demand.
- **Unmeasured multipliers.** Every number here comes from the pricing page or from
  `bench/` runs you can repeat.

Kept from it: scoring several dimensions instead of one "difficulty", escalating on
observed failure, and sending deterministic edits to a tool instead of a model.
