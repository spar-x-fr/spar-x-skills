# Settings worth knowing

Session effort default (`low` to `xhigh`; `max` is not accepted in this key):

```json
{ "effortLevel": "medium" }
```

Opus 5.5 already defaults to `medium` on the API. If your sessions run at `high`
all the time, check this key and `/effort`: `rightsize` raises effort per turn
(`ultrathink`) or per sub-agent when the task needs it.

Plan on Opus, execute on Sonnet, in one session:

```text
/model opusplan
```

Measure before and after a change:

```bash
python <rightsize>/scripts/token_audit.py --since 2026-10-01 --until 2026-10-15
python <rightsize>/scripts/token_audit.py --since 2026-10-15
```
