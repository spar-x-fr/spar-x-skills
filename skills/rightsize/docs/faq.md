# FAQ

## The rules do not show up

Ask a new session "What does rule 0 of rightsize say?". If it does not know:

1. `claude --version` must be 2.1.275 or later.
2. `/plugin` should list `rightsize` as enabled.
3. Python must run as `python3` or `python`. Test the hook by hand:
   `echo '{"hook_event_name":"SessionStart"}' | python3 hooks/inject.py`
   It should print JSON with `additionalContext`.
4. A setting such as `disableAllHooks` or an organisation policy can turn hooks off.

## Can I still change the effort myself?

Yes. The effort button (or `/effort`) sets your conversation's effort. Agents with an
`effort:` line keep theirs; to change one, say it in your message ("run tdd-guide at
high") or edit its file. See [Usage guide](usage-guide.md#effort-the-button-and-the-agents).

## Does it make Claude cheaper but worse?

It is built the other way round. Rule 0 is quality before optimisation: savings only
come from what does not touch the deliverable. Lower effort is used where a check
(tests, an oracle) proves the result, and a failure climbs the ladder. Work no check
can grade keeps a high effort. The measurements behind this are in
[Effort and models](effort-and-models.md).

## Why are my tests sometimes all run?

Because a shared or unclassified file changed, a changed file has no test mapped to
it, or the last full run is red or older than 7 days or 30 commits.
`python test_scope.py` prints the reason. See [Scoped testing](scoped-testing.md).

## The benchmark says "credit balance is too low"

Headless runs use the account `claude` is logged in with, which can be an API key
with prepaid credit rather than your subscription. Check with `claude auth status`;
`/login` switches account. The runner stops at the first such error.

## Many `git fsmonitor--daemon` processes appeared

With `core.fsmonitor=true` in your git config, every throwaway repository starts a
daemon. The test suite turns fsmonitor off for the repositories it creates; if you ran
an older version, stop the stale daemons (`git fsmonitor--daemon stop` in each repo, or
end the processes). They restart on their own where they are useful.

## Does any data leave my machine?

No. The hooks print text, the scripts read local files. The only network calls are
the ones Claude Code itself makes, and the benchmark runs you start.
