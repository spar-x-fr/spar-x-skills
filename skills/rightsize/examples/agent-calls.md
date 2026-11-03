# Agent calls with an explicit model and effort

Without `effort`, a sub-agent inherits the session effort: a search started from an
`xhigh` session searches at `xhigh`. Pass both fields when the tier differs.

```text
Agent(subagent_type="Explore", model="haiku", effort="low",
      description="Find backoff factor",
      prompt="Where is the retry backoff factor of the payment client defined? "
             "Answer with path:line and the value, under 80 words. Do not edit.")

Agent(subagent_type="rs-builder",            # sonnet / medium from its frontmatter
      description="Fix duration parser",
      prompt="Make test_durations.py pass. Invalid input raises ValueError. "
             "Run python -m unittest. Report files changed and the test result.")

Agent(subagent_type="rs-sage",               # opus / high
      description="Review migration safety",
      prompt="Review migrations/0042_users.py for data loss and lock risk on a "
             "40M-row table. Verified facts vs inferences, one recommendation.")
```
