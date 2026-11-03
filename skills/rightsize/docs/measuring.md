# Measuring

## Your own usage: `token_audit.py`

Reads the transcripts Claude Code keeps in `~/.claude/projects/` (main sessions and
sub-agents). Nothing leaves your machine.

```bash
python token_audit.py                                  # last 30 days
python token_audit.py --since 2026-10-01 --until 2026-11-01
python token_audit.py --project my-repo --json
```

It reports the total at list prices, the split by role (main thread / sub-agents),
model, effort and sub-agent type, the cache hit ratio, and two savings estimates:
read-only sub-agents that did not run on Haiku, and main-thread model switches that
re-wrote the cache. Responses from models without a known price are counted and
named, never silently priced at zero.

**What the dollars mean.** They are list prices of the API. If you use Claude Code
with a subscription, they are an equivalent, not an invoice; if you use an API key,
they are close to what you pay. Either way they compare periods fairly.

To measure rightsize itself, compare a period before installing it with a period
after, of similar work.

## The benchmark: `bench/`

`bench/run_bench.py` copies a task's repository into a fresh folder, runs Claude Code
headless with a given model and effort, grades the result with the task's checker and
appends one JSON line per run. `bench/summarize.py` turns the lines into tables.

```bash
python bench/run_bench.py --task t3-bugfix --model sonnet --effort medium --reps 3 --label mine
python bench/summarize.py bench/results.jsonl
```

| Task | What it checks |
|---|---|
| `t1-lookup` | find a value in a repository with decoys |
| `t2-rename` | rename a function across files and add type hints |
| `t3-bugfix` | fix a parser against hidden tests |
| `t4-algorithm` | optimal scheduler with precedence (Lawler), brute-force checked |
| `t5-composite` | the first three in one session, with or without the skill |
| `t6-subtle-bugs` | six subtle bugs in a weighted TTL LRU cache, 300 random sequences against a reference model |
| `t7-hard-algorithm` | tour with mandatory stops and a toll quota, exhaustive search on 250 graphs, a naive solution misses the time limit |
| `t8-regex-engine` | a regex engine without `re`, compared with `re` on 3 000 random patterns |

Every checker was validated before use: a reference solution passes, a buggy or naive
one fails.

### Before you run it

- **Every run spends real tokens.** With an API key that is real money: the October
  2026 sweep cost about $28.50 at list prices for 121 runs. Start with `--reps 1`.
- The runner stops at the first infrastructure error (no credit, usage limit, outage)
  instead of recording empty runs as failures.
- On Windows keep `--workdir` short (the default is `~/rs-bench`): some task paths hit
  the 260-character limit.

Published results: `bench/results/2026-10-30.jsonl` (routing, 19 runs) and
`bench/results/2026-10-31-effort-sweep.jsonl` (effort sweep, 100 valid runs), with a
Markdown summary next to each.
