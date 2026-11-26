# Expert playbooks

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

## Writing and published content (posts, emails, pages, product copy)

Published text is R = 2: the reader, not a test, grades it.

1. **Brief first**: who reads it, what they should do next, the one idea, the channel's
   limits (length, format, tone). Ask the user only what the material cannot answer.
2. **Facts from sources** (rs-scout, haiku/low): every figure, name, date and quote
   comes with its source. No source, no claim.
3. **Draft** on sonnet/medium; opus/high when the positioning or the argument is the
   hard part (A ≥ 2). One strong draft beats five variants nobody compares.
4. **Verify**: re-read as the target reader; check each fact against its source, each
   link by opening it, the length and format against the channel. Mechanical variants
   (translations, resizes) are BULK on haiku/low against the approved master.

## Data analysis and documents (spreadsheets, reports, decks)

1. **State the question and the unit** before touching the data; inspect the real
   rows (types, gaps, duplicates), not the header.
2. **Compute with code or formulas**, never in prose (T0 when a tool does it).
3. **Verify**: totals reconcile with the source, one figure is recomputed a second
   way, the file is opened and looked at as the reader will see it.
4. Say what was excluded and why, and which numbers are estimates.

## Actions in someone's name (messages, forms, purchases, posts, deletions)

Sending, publishing, paying and deleting cannot be taken back: handle them like the
irreversible steps of the migration playbook.

1. **Prepare everything reversible first**: research, drafts, the exact list of
   recipients or items, on the cheapest tier that a check covers.
2. **Show the user the exact action** (what, to whom, how many, what it costs) and get
   their go before the first irreversible step, unless they already gave it for this
   exact action.
3. **Execute one, verify, then batch**: confirm the first result where it lands before
   the rest. Stop at the first anomaly instead of retrying.
4. **Log** what was done, to whom and when, so a later run neither repeats nor skips.

## Scheduled or unattended run

Nobody answers questions and nobody watches: the brief carries everything.

1. A standalone prompt: goal, inputs, the check, the limits, what to do when blocked.
2. **Idempotent**: read the log of the previous runs first; never do the same item twice.
3. **Hard caps** on volume, spend and duration; stop and report when one is reached.
4. Anything irreversible and ambiguous is prepared and left for the user, not guessed.
5. End with a short report: done, skipped and why, blocked, what the next run needs.

## Sprint close

1. `test_scope.py --full --run` and record the result in the ledger.
2. Re-run anything flagged `unmapped` during the sprint and add the missing tests.
3. Write what was learned (decisions, traps, measured numbers) to memory or the
   project's docs, not to chat only.
