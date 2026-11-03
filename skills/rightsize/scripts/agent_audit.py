#!/usr/bin/env python3
"""List sub-agent definitions without `model` / `effort` and suggest values.

An agent without `effort` inherits the session effort, so a search agent started
from an xhigh session searches at xhigh. This script only reads, unless --apply.

    python agent_audit.py                  # ~/.claude/agents and ./.claude/agents
    python agent_audit.py --dir path/to/agents
    python agent_audit.py --apply          # add the missing fields, keeps a .bak copy
"""

import argparse
import re
import shutil
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# First match wins. Judgment-heavy roles stay on strong tiers; reading and
# mechanical roles drop to cheap ones.
ROLE_RULES = (
    (r"secur|architect|bar.?raiser|shogun|planner", "opus", "high"),
    (r"review|kensa|critic|audit", "sonnet", "high"),
    (r"explor|scout|search|lookup|docs?-|kage|scraper|harvest", "haiku", "low"),
    (r"doc|codemap|readme|changelog|status.?line", "haiku", "medium"),
    (r"build|resolver|fix|refactor|clean", "sonnet", "medium"),
    (r"test|tdd|e2e", "sonnet", "medium"),
)
DEFAULT = ("sonnet", "medium")
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---", re.DOTALL)


@dataclass(frozen=True)
class Agent:
    path: Path
    name: str
    model: Optional[str]
    effort: Optional[str]
    suggested_model: str
    suggested_effort: str


def field(block: str, key: str) -> Optional[str]:
    match = re.search(rf"^{key}:\s*(.+?)\s*$", block, re.MULTILINE)
    return match.group(1).strip("'\"") if match else None


def suggest(name: str, description: str) -> tuple[str, str]:
    # The name is the strongest signal; descriptions mention many roles in passing
    # ("no architectural edits"), so only their first sentence is a fallback.
    first_sentence = description.split(".")[0].lower()
    for text in (name.lower(), first_sentence):
        for pattern, model, effort in ROLE_RULES:
            if re.search(rf"\b(?:{pattern})", text):  # "research" is not "search"
                return model, effort
    return DEFAULT


def load(path: Path) -> Optional[Agent]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as err:
        print(f"[warn] lecture impossible {path}: {err}", file=sys.stderr)
        return None
    match = FRONTMATTER.match(text)
    if not match:
        return None
    block = match.group(1)
    name = field(block, "name") or path.stem
    model, effort = suggest(name, field(block, "description") or "")
    return Agent(path, name, field(block, "model"), field(block, "effort"), model, effort)


def add_missing(agent: Agent) -> bool:
    """Add the missing fields, re-reading the file so a second pass is a no-op.
    newline="" keeps the file's own line endings; an existing .bak is never replaced,
    so it always holds the original."""
    with agent.path.open(encoding="utf-8", newline="") as handle:
        text = handle.read()
    match = FRONTMATTER.match(text)
    if not match:
        return False
    block = match.group(1)
    lines = []
    if not field(block, "model"):
        lines.append(f"model: {agent.suggested_model}")
    if not field(block, "effort"):
        lines.append(f"effort: {agent.suggested_effort}")
    if not lines:
        return False
    newline = "\r\n" if "\r\n" in text[: match.end()] else "\n"
    end = match.end() - 3  # just before the closing ---
    updated = text[:end] + newline.join(lines) + newline + text[end:]
    backup = agent.path.with_suffix(agent.path.suffix + ".bak")
    if not backup.exists():
        shutil.copy2(agent.path, backup)
    with agent.path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    return True


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dir",
        action="append",
        help="agents folder (repeatable); default: user and project folders",
    )
    parser.add_argument("--apply", action="store_true", help="write the missing fields")
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    candidates = (
        [Path(d) for d in args.dir]
        if args.dir
        else [Path.home() / ".claude" / "agents", Path.cwd() / ".claude" / "agents"]
    )
    # Same folder twice (repeated --dir, or run from the home folder) must load once.
    folders = list(dict.fromkeys(f.resolve() for f in candidates if f.is_dir()))
    agents = [a for folder in folders for a in map(load, sorted(folder.glob("*.md"))) if a]
    if not agents:
        print("Aucun agent trouvé.", file=sys.stderr)
        return 1

    missing = [a for a in agents if not a.model or not a.effort]
    print(
        f"{len(agents)} agents · {sum(not a.model for a in agents)} sans model"
        f" · {sum(not a.effort for a in agents)} sans effort\n"
    )
    for a in missing:
        current = f"{a.model or '—'} / {a.effort or '—'}"
        proposal = f"{a.model or a.suggested_model} / {a.effort or a.suggested_effort}"
        print(f"  {a.name:<28} actuel {current:<18} proposé {proposal}")
    if args.apply:
        changed = sum(add_missing(a) for a in missing)
        print(f"\n{changed} fichiers modifiés (copie .bak à côté de chacun).")
    elif missing:
        print("\nRelisez les propositions, puis relancez avec --apply pour les écrire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
