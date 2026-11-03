# Getting started

## Requirements

- Claude Code **2.1.275 or later** (agent `effort:` frontmatter and the one-line
  plugin install). Check with `claude --version`; update with your installer
  (`npm install -g @anthropic-ai/claude-code@latest` for npm installs).
- Python **3.9+** on your `PATH` as `python3` or `python`. Standard library only.
- `git`, for scoped testing.

## Install as a plugin (recommended)

In Claude Code:

```text
/plugin marketplace add spar-x-fr/spar-x-skills
/plugin install spar-x-skills@spar-x-skills
```

This installs the skill, the four `rs-*` agents and the hooks that make the rules
apply in every session and every sub-agent. Nothing to merge by hand.

## Check that it is active

Start a new session and ask:

```text
What does rule 0 of rightsize say?
```

The answer should quote **quality before optimisation**. That text comes from the
SessionStart hook; if it is missing, see [FAQ](faq.md#the-rules-do-not-show-up).

## Manual install (without the plugin system)

```bash
git clone https://github.com/spar-x-fr/spar-x-skills.git ~/spar-x-skills
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r ~/spar-x-skills/skills/rightsize ~/.claude/skills/
cp ~/spar-x-skills/skills/rightsize/agents/*.md ~/.claude/agents/
```

Then add the hooks to `~/.claude/settings.json`, merged with any `hooks` you
already have, pointing at the installed skill:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [{ "type": "command", "command": "python3 ~/.claude/skills/rightsize/hooks/inject.py", "timeout": 10 }] }
    ],
    "PreToolUse": [
      { "matcher": "Agent",
        "hooks": [{ "type": "command", "command": "python3 ~/.claude/skills/rightsize/hooks/inject.py", "timeout": 10 }] }
    ]
  }
}
```

On Windows use `python` and a full path such as `C:/Users/you/.claude/skills/rightsize/hooks/inject.py`.

## Optional: give your existing agents an effort level

Agents without `effort:` inherit the session effort, so a search agent started from
a `high` session searches at `high`. Review the proposals first; nothing is written:

```bash
python <rightsize>/scripts/agent_audit.py
```

Then write them, with a `.bak` copy of every file:

```bash
python <rightsize>/scripts/agent_audit.py --apply
```

Agents that handle money, legal text, security or anything published deserve
`high` even when the tool proposes less: raise them by hand. See
[Agents and protocol](agents-and-protocol.md).

## Uninstall

```text
/plugin uninstall rightsize
```

For a manual install, delete the copied folders and the two hook entries. Agent
files changed by `agent_audit.py --apply` can be restored from their `.bak` copies.
