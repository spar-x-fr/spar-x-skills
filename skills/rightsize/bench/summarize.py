#!/usr/bin/env python3
"""Summarise bench results as a Markdown table: pass rate and mean cost per config.

python summarize.py results.jsonl
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Optional, Union

Row = dict[str, Any]
Stats = dict[tuple[str, str], tuple[float, int, int]]


def load(path: Union[str, Path]) -> list[Row]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def models_used(row: Row) -> str:
    return "+".join(sorted(m.replace("claude-", "") for m in (row.get("model_usage") or {})))


def summarize(rows: list[Row]) -> tuple[str, Stats]:
    groups: defaultdict[tuple[str, str, str, str], list[Row]] = defaultdict(list)
    for row in rows:
        groups[(row["task"], row["label"], row["model"], row["effort"])].append(row)
    lines = [
        "| "
        + " | ".join(
            (
                "Tâche",
                "Config",
                "Modèle/effort",
                "Réussite",
                "Coût moyen",
                "Tokens sortie",
                "Tours",
                "Durée",
                "Modèles appelés",
            )
        )
        + " |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    stats: Stats = {}
    for (task, label, model, effort), items in sorted(groups.items()):
        cost = mean(r["cost_usd"] or 0 for r in items)
        out = mean((r.get("usage") or {}).get("output_tokens", 0) for r in items)
        passed = sum(r["passed"] for r in items)
        stats[(task, label)] = (cost, passed, len(items))
        lines.append(
            f"| {task} | {label} | {model}/{effort} | {passed}/{len(items)} | "
            f"{cost:.4f} $ | {out:,.0f} | {mean(r['turns'] or 0 for r in items):.1f} | "
            f"{mean(r['wall_s'] or 0 for r in items):.0f} s | "
            f"{', '.join(sorted({models_used(r) for r in items}))} |"
        )
    return "\n".join(lines), stats


def comparisons(stats: Stats) -> str:
    lines = ["", "| Tâche | Comparaison | Coût | Écart | Réussite |", "|---|---|---|---|---|"]
    for (task, label), (cost, passed, n) in sorted(stats.items()):
        if label == "baseline":
            continue
        base = stats.get((task, "baseline"))
        if not base:
            continue
        change = (cost - base[0]) / base[0] if base[0] else 0
        lines.append(
            f"| {task} | {label} vs baseline | {cost:.4f} $ vs {base[0]:.4f} $ | "
            f"{change:+.0%} | {passed}/{n} vs {base[1]}/{base[2]} |"
        )
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print(__doc__, file=sys.stderr)
        return 2
    table, stats = summarize(load(argv[0]))
    print(table)
    print(comparisons(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
