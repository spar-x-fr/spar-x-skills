#!/usr/bin/env python3
"""Measure where Claude Code tokens and dollars actually go, from local transcripts.

Reads ~/.claude/projects/<project>/<session>.jsonl and the sub-agent transcripts
in <session>/subagents/. Nothing is sent anywhere.

    python token_audit.py                      # last 30 days, all projects
    python token_audit.py --since 2026-10-01 --project MyRepo
    python token_audit.py --session <uuid> --json

Costs are list prices (see prices.py), not what a subscription bills. The
"what-if" savings assume the cheaper model would have used the same number of
tokens, which is an estimate, not a measurement.
"""

import argparse
import json
import sys
from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional, cast

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prices import request_cost

READ_ONLY_TOOLS = frozenset(
    {
        "Read",
        "Grep",
        "Glob",
        "LS",
        "WebFetch",
        "WebSearch",
        "NotebookRead",
        "ToolSearch",
        "TodoWrite",
    }
)
CHEAP_MODEL = "claude-haiku-5-5"


@dataclass(frozen=True)
class Turn:
    session: str
    project: str
    agent_id: Optional[str]
    agent_type: Optional[str]
    model: str
    effort: Optional[str]
    timestamp: str
    usage: dict[str, Any]
    tools: tuple[Any, ...]
    cost: float
    priced: bool = True
    msg_id: str = ""


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(Path.home() / ".claude" / "projects"))
    parser.add_argument("--since", help="YYYY-MM-DD (default: 30 days ago)")
    parser.add_argument("--until", help="YYYY-MM-DD, exclusive")
    parser.add_argument("--project", help="substring of the project folder name")
    parser.add_argument("--session", help="session id (prefix accepted)")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    parser.add_argument("--top", type=int, default=8)
    return parser.parse_args(argv)


def default_since() -> str:
    return (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")


def transcript_files(root: Path, project: Optional[str], session: Optional[str]) -> Iterator[Path]:
    if not root.is_dir():
        raise SystemExit(f"Dossier introuvable : {root}")
    for project_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        if project and project.lower() not in project_dir.name.lower():
            continue
        for path in project_dir.rglob("*.jsonl"):
            if session and not _session_of(path).startswith(session):
                continue
            yield path


def _session_of(path: Path) -> str:
    return path.parent.parent.name if path.parent.name == "subagents" else path.stem


def _agent_type(path: Path) -> Optional[str]:
    meta = path.with_suffix(".meta.json")
    if not meta.exists():
        return None
    try:
        return cast(Optional[str], json.loads(meta.read_text(encoding="utf-8")).get("agentType"))
    except (OSError, json.JSONDecodeError):
        return None


def read_turns(path: Path, since: str, until: Optional[str]) -> Iterator[Turn]:
    """One Turn per API response. Claude Code writes one line per content block,
    all carrying the same usage, so responses are de-duplicated by message id."""
    try:
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%d")
    except OSError as err:
        print(f"[warn] lecture impossible {path}: {err}", file=sys.stderr)
        return
    if modified < since:  # untouched since the window opened: nothing newer inside
        return
    is_sub = path.parent.name == "subagents"
    agent_type = _agent_type(path) if is_sub else None
    seen: dict[str, Turn] = {}
    for line in _lines(path):  # streamed: transcripts reach hundreds of megabytes
        if '"assistant"' not in line:
            continue
        record = _parse(line)
        if not record or record.get("type") != "assistant":
            continue
        message = record.get("message") or {}
        usage, msg_id = message.get("usage"), message.get("id")
        stamp = record.get("timestamp", "")
        if not usage or not msg_id or stamp[:10] < since or (until and stamp[:10] >= until):
            continue
        tools = tuple(
            b.get("name")
            for b in message.get("content") or []
            if isinstance(b, dict) and b.get("type") == "tool_use"
        )
        if msg_id in seen:
            seen[msg_id] = merge(seen[msg_id], usage, tools)
            continue
        model = message.get("model") or ""
        if model == "<synthetic>":  # written locally by Claude Code, no API call
            continue
        cost = request_cost(model, usage)
        seen[msg_id] = Turn(
            session=_session_of(path),
            project=path.parents[2 if is_sub else 0].name,
            # A sub-agent file without agentId must not look like the main thread.
            agent_id=(record.get("agentId") or path.stem) if is_sub else None,
            agent_type=agent_type,
            model=model,
            effort=record.get("effort"),
            timestamp=stamp,
            usage=usage,
            tools=tools,
            cost=cost or 0.0,
            priced=cost is not None,
            msg_id=msg_id,
        )
    yield from seen.values()


def _lines(path: Path) -> Iterator[str]:
    try:
        with path.open(encoding="utf-8", errors="replace") as handle:
            yield from handle
    except OSError as err:
        print(f"[warn] lecture impossible {path}: {err}", file=sys.stderr)


def merge(turn: Turn, usage: dict[str, Any], tools: tuple[Any, ...]) -> Turn:
    """Later lines of a streamed response can carry the final usage: keep the larger."""
    final = (
        usage
        if (usage.get("output_tokens") or 0) > (turn.usage.get("output_tokens") or 0)
        else turn.usage
    )
    cost = request_cost(turn.model, final) if final is not turn.usage else None
    return replace(
        turn, usage=final, tools=turn.tools + tools, cost=turn.cost if cost is None else cost
    )


def dedupe(turns: Iterable[Turn]) -> list[Turn]:
    """Resumed or forked sessions copy earlier messages into a new file; count each
    API response once across all files."""
    unique: dict[str, Turn] = {}
    for turn in turns:
        unique.setdefault(turn.msg_id, turn)
    return list(unique.values())


def _parse(line: str) -> Optional[dict[str, Any]]:
    try:
        return cast(Optional[dict[str, Any]], json.loads(line))
    except json.JSONDecodeError:
        return None


def tokens(turns: Iterable[Turn]) -> dict[str, Any]:
    totals: defaultdict[str, Any] = defaultdict(int)
    for turn in turns:
        for key in (
            "input_tokens",
            "cache_creation_input_tokens",
            "cache_read_input_tokens",
            "output_tokens",
        ):
            totals[key] += turn.usage.get(key, 0) or 0
    prompt = (
        totals["input_tokens"]
        + totals["cache_creation_input_tokens"]
        + totals["cache_read_input_tokens"]
    )
    totals["cache_hit_ratio"] = (
        round(totals["cache_read_input_tokens"] / prompt, 3) if prompt else 0
    )
    return dict(totals)


def group(turns: Iterable[Turn], key: Callable[[Turn], str]) -> dict[str, Any]:
    buckets: defaultdict[str, list[Turn]] = defaultdict(list)
    for turn in turns:
        buckets[key(turn)].append(turn)
    return {
        name: {"turns": len(items), "cost": round(sum(t.cost for t in items), 2), **tokens(items)}
        for name, items in sorted(buckets.items(), key=lambda kv: -sum(t.cost for t in kv[1]))
    }


def readonly_subagent_savings(turns: Iterable[Turn]) -> dict[str, Any]:
    """Sub-agents that only read, yet ran on a model pricier than Haiku."""
    by_agent: defaultdict[tuple[str, str], list[Turn]] = defaultdict(list)
    for turn in turns:
        if turn.agent_id:
            by_agent[(turn.session, turn.agent_id)].append(turn)
    candidates: list[dict[str, Any]] = []
    saved = 0.0
    for (_, agent_id), items in by_agent.items():
        used = {name for t in items for name in t.tools}
        if not used or not used <= READ_ONLY_TOOLS or all("haiku" in t.model for t in items):
            continue
        actual = sum(t.cost for t in items)
        cheap = sum(request_cost(CHEAP_MODEL, t.usage) or 0 for t in items)
        if cheap >= actual:  # nothing to gain, or the model is unpriced
            continue
        saved += actual - cheap
        candidates.append(
            {
                "agent": agent_id,
                "type": items[0].agent_type,
                "model": items[0].model,
                "cost": round(actual, 3),
                "if_haiku": round(cheap, 3),
            }
        )
    candidates.sort(key=lambda c: c["if_haiku"] - c["cost"])
    return {
        "count": len(candidates),
        "estimated_saving": round(saved, 2),
        "examples": candidates[:5],
    }


def model_switches(turns: Iterable[Turn]) -> dict[str, Any]:
    """Main-thread model changes inside a session: each one re-writes the cache."""
    by_session: defaultdict[str, list[Turn]] = defaultdict(list)
    for turn in turns:
        if not turn.agent_id:
            by_session[turn.session].append(turn)
    switches, rewrite_cost = 0, 0.0
    for items in by_session.values():
        items.sort(key=lambda t: t.timestamp)
        for before, after in zip(items, items[1:]):
            if before.model and after.model and before.model != after.model:
                switches += 1
                written = after.usage.get("cache_creation_input_tokens", 0) or 0
                rewrite_cost += (
                    request_cost(after.model, {"cache_creation_input_tokens": written}) or 0
                )
    return {"switches": switches, "cache_rewrite_cost": round(rewrite_cost, 2)}


def build_report(turns: list[Turn], args: argparse.Namespace) -> dict[str, Any]:
    total = sum(t.cost for t in turns)
    sessions = group(turns, lambda t: t.session)
    return {
        "window": {"since": args.since, "until": args.until, "project": args.project},
        "total_cost": round(total, 2),
        "unpriced": {
            "responses": sum(not t.priced for t in turns),
            "models": sorted({t.model for t in turns if not t.priced}),
        },
        "responses": len(turns),
        "sessions": len(sessions),
        "tokens": tokens(turns),
        "by_role": group(turns, lambda t: "sous-agent" if t.agent_id else "principal"),
        "by_model": group(turns, lambda t: t.model or "?"),
        "by_effort": group(turns, lambda t: t.effort or "?"),
        "by_agent_type": group([t for t in turns if t.agent_id], lambda t: t.agent_type or "?"),
        "top_sessions": dict(list(sessions.items())[: args.top]),
        "opportunities": {
            "readonly_subagents_not_on_haiku": readonly_subagent_savings(turns),
            "main_thread_model_switches": model_switches(turns),
        },
    }


def print_text(report: dict[str, Any], top: int) -> None:
    tok = report["tokens"]
    print(
        f"Fenêtre : depuis {report['window']['since']}"
        f"{' jusqu’à ' + report['window']['until'] if report['window']['until'] else ''}"
        f"{' · projet ' + report['window']['project'] if report['window']['project'] else ''}"
    )
    print(
        f"Coût au prix catalogue : {report['total_cost']:.2f} $ · {report['responses']} réponses"
        f" · {report['sessions']} sessions · cache {tok['cache_hit_ratio']:.0%} des tokens d'entrée"
    )
    for title, key in (
        ("Par rôle", "by_role"),
        ("Par modèle", "by_model"),
        ("Par effort", "by_effort"),
        ("Sous-agents par type", "by_agent_type"),
    ):
        print(f"\n{title}")
        for name, row in list(report[key].items())[:top]:
            share = row["cost"] / report["total_cost"] if report["total_cost"] else 0
            print(
                f"  {name:<28} {row['cost']:>9.2f} $  {share:>4.0%}  {row['turns']:>6} rép."
                f"  sortie {row['output_tokens']:>10,}  cache {row['cache_hit_ratio']:.0%}"
            )
    ro = report["opportunities"]["readonly_subagents_not_on_haiku"]
    sw = report["opportunities"]["main_thread_model_switches"]
    print("\nPistes d'économie (estimations)")
    print(
        f"  Sous-agents en lecture seule hors Haiku : {ro['count']}"
        f" → économie estimée {ro['estimated_saving']:.2f} $ s'ils avaient tourné sur Haiku 5.5"
    )
    print(
        f"  Changements de modèle dans le fil principal : {sw['switches']}"
        f" → réécriture du cache {sw['cache_rewrite_cost']:.2f} $"
    )
    unpriced = report["unpriced"]
    if unpriced["responses"]:
        print(
            f"\n[attention] {unpriced['responses']} réponses de modèles sans prix connu, "
            f"non comptées : {', '.join(unpriced['models'])} (ajoutez-les dans prices.py)"
        )


def main(argv: Optional[Sequence[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):  # a piped cp1252 stdout cannot print "→"
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args(argv)
    args.since = args.since or default_since()
    turns = dedupe(
        turn
        for path in transcript_files(Path(args.root), args.project, args.session)
        for turn in read_turns(path, args.since, args.until)
    )
    if not turns:
        print("Aucune réponse trouvée pour ces filtres.", file=sys.stderr)
        return 1
    report = build_report(turns, args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_text(report, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
