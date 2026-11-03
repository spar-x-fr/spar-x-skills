#!/usr/bin/env python3
"""rightsize hook for SessionStart and PreToolUse(Agent).

SessionStart: puts the rightsize rules in front of every session, once.
PreToolUse on the Agent tool: appends the sub-agent rules to the brief. On Claude
Code 2.1.308 a SubagentStart hook's context did not reach the sub-agent, so the
rules travel inside its prompt instead (verified in a sub-agent transcript).

Prints Claude Code hook JSON on stdout. Never fails the session: on any error it
prints nothing and exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def scripts_dir() -> Path:
    """Works installed as a plugin (hooks/ next to skills/) or as a bare skill."""
    for candidate in (HERE.parent / "skills" / "rightsize" / "scripts", HERE.parent / "scripts"):
        if (candidate / "test_scope.py").exists():
            return candidate
    return HERE.parent / "skills" / "rightsize" / "scripts"


TEST_SCOPE = (scripts_dir() / "test_scope.py").as_posix()

MAIN = f"""RIGHTSIZE is active (skill: rightsize).
Rule 0, above everything: QUALITY BEFORE OPTIMISATION.
The deliverable must reach elite expert quality; savings never come from weaker reasoning on it.
Optimise only what does not touch quality: no useless parallelism, no re-reading, no full test run
when only one module changed, cheap models for lookups and mechanical steps.
- Before non-trivial work, load the rightsize skill and follow its playbook for the work type.
- Every Agent call: pass `model` and `effort` deliberately, and brief it with the hand-off format.
- Tests: run `python "{TEST_SCOPE}" --run` during work;
  `--full --run` at the end of a sprint or before a release, and record the result.
- Never stop at the first plausible answer: verify it, find the root cause, then report."""

SUB = f"""RIGHTSIZE rules for this sub-agent. QUALITY BEFORE OPTIMISATION.
- Do the job to elite expert standard: verify claims against the code or a run, find root causes.
- Stay inside your brief; do not widen scope. If the brief is missing something decisive, say so.
- If you fail twice the same way, stop and report instead of guessing.
- Scoped tests: `python "{TEST_SCOPE}" --run` (add `--full` when the brief says the work is done).
- Reply in the hand-off format: STATUS (done / partial / blocked), RESULT, EVIDENCE (file:line,
  commands and their output), CONFIDENCE (high / medium / low and why), NEXT (what is left)."""


def brief_with_rules(payload: dict[str, Any]) -> dict[str, Any]:
    """PreToolUse on Agent: append the sub-agent rules to the brief, once."""
    tool_input = payload.get("tool_input") or {}
    prompt = tool_input.get("prompt")
    if not isinstance(prompt, str) or "RIGHTSIZE" in prompt:
        return {}
    updated = {**tool_input, "prompt": f"{prompt}\n\n---\n{SUB}"}
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": updated}}


def main() -> int:
    # Claude Code sends UTF-8; the locale decoder (cp1252 on Windows) would mangle
    # every accent in the sub-agent brief it hands back.
    raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    try:
        payload = json.loads(raw or "{}")
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    event = payload.get("hook_event_name") or (sys.argv[1] if len(sys.argv) > 1 else "SessionStart")
    if event == "PreToolUse":
        output = brief_with_rules(payload)
        if output:
            print(json.dumps(output))
        return 0
    context = SUB if event == "SubagentStart" else MAIN
    print(
        json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}})
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # a broken hook must never block a session
        sys.exit(0)
