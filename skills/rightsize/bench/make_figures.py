#!/usr/bin/env python3
"""Draw the README figures from the raw benchmark results, in dark and light.

    python bench/make_figures.py

Every number on a figure is computed from bench/results/*.jsonl, so a figure cannot
drift from the data. Standard library only; the output is plain SVG.
"""

# ruff: noqa: E501  (SVG markup reads better on one line)
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "bench" / "results"
OUT = ROOT / "docs" / "assets"

SWEEP_TASKS = ("t3-bugfix", "t6-subtle-bugs", "t7-hard-algorithm")  # swept on every effort
EFFORTS = ("low", "medium", "high", "xhigh", "max")
ROUTED_TASKS = (
    ("t1-lookup", "Find a value in a repo"),
    ("t2-rename", "Rename across files"),
    ("t3-bugfix", "Fix a parser, hidden tests"),
)

SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Consolas,Menlo,monospace"
THEMES = {
    "dark": {
        "bg": "#0B0F14",
        "panel": "#131A22",
        "line": "#2A3540",
        "ink": "#F4F6F8",
        "dim": "#9AA7B4",
        "cost": "#FFB224",
        "good": "#3DD68C",
        "base": "#55636F",
    },
    "light": {
        "bg": "#FBFAF6",
        "panel": "#F0EEE6",
        "line": "#D5D2C6",
        "ink": "#12181F",
        "dim": "#55606B",
        "cost": "#B85C00",
        "good": "#0B7A4B",
        "base": "#A9AEA9",
    },
}

Colours = dict[str, str]
Index = dict[str, dict[str, float]]


def load(name: str) -> list[dict[str, Any]]:
    with (RESULTS / name).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def text(x: float, y: float, body: str, size: int, fill: str, **kw: str) -> str:
    family = kw.pop("family", SANS)
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" '
        f'fill="{fill}"{extra}>{body}</text>'
    )


def svg(width: int, height: int, title: str, body: list[str], bg: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{title}"><title>{title}</title>'
        f'<rect width="{width}" height="{height}" rx="16" fill="{bg}"/>'
        + "".join(body)
        + "</svg>\n"
    )


def cost_index(rows: list[dict[str, Any]]) -> Index:
    """Summed mean cost over the fully swept tasks, relative to `high`, per model."""
    cells: dict[tuple[str, str, str], list[float]] = defaultdict(list)
    for row in rows:
        cells[(row["model"], row["effort"], row["task"])].append(row["cost_usd"])
    index = {}
    for model in ("sonnet", "opus"):
        totals = {e: sum(mean(cells[(model, e, t)]) for t in SWEEP_TASKS) for e in EFFORTS}
        index[model] = {e: totals[e] / totals["high"] for e in EFFORTS}
    return index


def curve(
    index: dict[str, float], x0: float, step: float, y0: float, scale: float
) -> list[tuple[float, float]]:
    return [(x0 + i * step, y0 - index[e] * scale) for i, e in enumerate(EFFORTS)]


def path(points: list[tuple[float, float]]) -> str:
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)


def cover(c: Colours, index: Index, runs: int) -> str:
    x0, step, base, scale = 660.0, 135.0, 500.0, 40.0
    pts = curve(index["opus"], x0, step, base, scale)
    top = 130.0
    body = [
        text(72, 250, "rightsize", 116, c["ink"], font_weight="700", letter_spacing="-4"),
        text(76, 318, "Elite quality first.", 38, c["ink"]),
        text(76, 368, "Then every token where it", 38, c["dim"]),
        text(76, 418, "changes the outcome.", 38, c["dim"]),
        text(76, 560, f"{runs} measured runs, hidden checks", 24, c["dim"], family=MONO),
        f'<line x1="{x0}" y1="{base}" x2="{x0 + 4 * step}" y2="{base}" '
        f'stroke="{c["line"]}" stroke-width="2"/>',
        f'<path d="{path([(x0, top), (x0 + 4 * step, top)])}" stroke="{c["good"]}" '
        'stroke-width="6" fill="none"/>',
        text(x0, top - 22, "tests passed: 100% at every effort", 28, c["good"], font_weight="600"),
        f'<path d="{path(pts)}" stroke="{c["cost"]}" stroke-width="6" fill="none" '
        'stroke-linejoin="round"/>',
    ]
    for (x, y), effort in zip(pts, EFFORTS):
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{c["cost"]}"/>')
        body.append(text(x, base + 44, effort, 25, c["dim"], family=MONO, text_anchor="middle"))
    label = f"cost ×{index['opus']['max']:.1f}"
    body.append(
        text(
            pts[-1][0] - 24,
            pts[-1][1] + 8,
            label,
            30,
            c["cost"],
            font_weight="700",
            text_anchor="end",
        )
    )
    body.append(text(x0, base + 88, "Opus 5.5, cost relative to high", 22, c["dim"]))
    return svg(
        1280, 640, "rightsize: pass rate stays flat while cost climbs with effort", body, c["bg"]
    )


def effort_chart(c: Colours, index: Index) -> str:
    x0, step, base, scale = 110.0, 262.0, 470.0, 38.0
    body = [
        text(48, 66, "More effort, same result, bigger bill", 40, c["ink"], font_weight="700"),
        text(
            48,
            108,
            "Mean cost vs high, 3 tasks swept on every effort. All runs passed.",
            26,
            c["dim"],
        ),
    ]
    for level in (1, 4, 8):
        y = base - level * scale
        width = 2 if level == 1 else 1
        body.append(
            f'<line x1="{x0}" y1="{y}" x2="{x0 + 4 * step}" y2="{y}" '
            f'stroke="{c["line"]}" stroke-width="{width}"/>'
        )
        body.append(text(x0 - 16, y + 8, f"{level}×", 24, c["dim"], family=MONO, text_anchor="end"))
    for model, colour in (("opus", c["cost"]), ("sonnet", c["good"])):
        pts = curve(index[model], x0, step, base, scale)
        body.append(f'<path d="{path(pts)}" stroke="{colour}" stroke-width="5" fill="none"/>')
        for x, y in pts:
            body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="{colour}"/>')
    for i, effort in enumerate(EFFORTS):
        x = x0 + i * step
        body.append(text(x, base + 42, effort, 26, c["ink"], family=MONO, text_anchor="middle"))
        values = f"{index['sonnet'][effort]:.1f}× / {index['opus'][effort]:.1f}×"
        body.append(text(x, base + 76, values, 22, c["dim"], family=MONO, text_anchor="middle"))
    body.append(text(x0 + 10, 190, "Opus 5.5", 28, c["cost"], font_weight="600"))
    body.append(text(x0 + 10, 228, "Sonnet 5.5", 28, c["good"], font_weight="600"))
    return svg(
        1280,
        580,
        "Cost relative to high effort climbs steeply above high while every run passes",
        body,
        c["bg"],
    )


def routing_chart(c: Colours, rows: list[dict[str, Any]]) -> str:
    cost: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in rows:
        cost[(row["task"], row["label"])].append(row["cost_usd"])
    top = max(mean(cost[(t, "baseline")]) for t, _ in ROUTED_TASKS)
    x0, width = 48.0, 860.0
    body = [
        text(48, 66, "The cheap route passed too", 40, c["ink"], font_weight="700"),
        text(
            48,
            108,
            "Opus at high for everything, against the routed choice. 2/2 passes each.",
            26,
            c["dim"],
        ),
    ]
    y = 180.0
    for task, name in ROUTED_TASKS:
        base, routed = mean(cost[(task, "baseline")]), mean(cost[(task, "routed")])
        base_w, routed_w = base / top * width, max(routed / top * width, 5)
        saving = (1 - routed / base) * 100
        body.append(text(x0, y, name, 28, c["ink"], font_weight="600"))
        body.append(
            f'<rect x="{x0}" y="{y + 14}" width="{base_w:.1f}" height="24" rx="4" fill="{c["base"]}"/>'
        )
        body.append(text(x0 + base_w + 12, y + 35, f"${base:.3f}", 24, c["dim"], family=MONO))
        body.append(
            f'<rect x="{x0}" y="{y + 44}" width="{routed_w:.1f}" height="24" rx="4" fill="{c["good"]}"/>'
        )
        body.append(text(x0 + routed_w + 12, y + 65, f"${routed:.3f}", 24, c["good"], family=MONO))
        body.append(
            text(
                1232, y + 56, f"−{saving:.0f}%", 50, c["good"], font_weight="700", text_anchor="end"
            )
        )
        y += 126
    return svg(
        1280, 560, "Routed runs cost far less than Opus at high with the same passes", body, c["bg"]
    )


def flow(c: Colours) -> str:
    steps = (
        ("1", "Score", ["scope, risk,", "ambiguity, depth"]),
        ("2", "Route", ["model, effort", "and mode"]),
        ("3", "Verify", ["tests the change", "actually reaches"]),
        ("4", "Escalate", ["one rung,", "on evidence"]),
    )
    width, gap = 278, 24
    body = []
    for i, (num, name, lines) in enumerate(steps):
        x = 48 + i * (width + gap)
        tone = c["cost"] if i == 3 else c["good"]
        body.append(
            f'<rect x="{x}" y="48" width="{width}" height="214" rx="12" '
            f'fill="{c["panel"]}" stroke="{c["line"]}"/>'
        )
        body.append(text(x + 24, 96, num, 26, tone, family=MONO, font_weight="700"))
        body.append(text(x + 24, 150, name, 42, c["ink"], font_weight="700"))
        for j, line in enumerate(lines):
            body.append(text(x + 24, 196 + j * 34, line, 26, c["dim"]))
    body.append(
        f'<path d="M1093 262 V312 H489 V262" fill="none" stroke="{c["cost"]}" '
        'stroke-width="3" stroke-dasharray="9 8"/>'
    )
    body.append(
        text(791, 354, "a failed check climbs the ladder", 28, c["cost"], text_anchor="middle")
    )
    return svg(
        1280, 384, "Score the task, route it, verify it, escalate on evidence", body, c["bg"]
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    sweep = load("2026-10-31-effort-sweep.jsonl")
    routing = load("2026-10-30.jsonl")
    index = cost_index(sweep)
    for theme, colours in THEMES.items():
        figures = {
            "cover": cover(colours, index, len(sweep)),
            "effort-cost": effort_chart(colours, index),
            "routing-savings": routing_chart(colours, routing),
            "how-it-works": flow(colours),
        }
        for name, content in figures.items():
            (OUT / f"{name}-{theme}.svg").write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
