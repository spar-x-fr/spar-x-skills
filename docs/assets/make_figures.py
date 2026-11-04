#!/usr/bin/env python3
"""Draw the root README figures, in dark and light.

    python docs/assets/make_figures.py

The measured numbers come from skills/rightsize/bench/results, through the figure
helpers of the rightsize project, so they cannot drift from the data.
"""

import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills" / "rightsize" / "bench"))

from make_figures import MONO, THEMES, cost_index, load, svg, text  # noqa: E402

OUT = ROOT / "docs" / "assets"
INSTALL = (
    "/plugin marketplace add spar-x-fr/spar-x-skills",
    "/plugin install spar-x-skills@spar-x-skills",
)


def cover(c: dict[str, str]) -> str:
    body = [
        text(72, 150, "spar-x-skills", 112, c["ink"], font_weight="700", letter_spacing="-4"),
        text(76, 222, "Des skills Claude Code prêtes pour la production", 40, c["ink"]),
        text(76, 276, "La qualité d'abord, l'économie ensuite. Par Spar-x.", 32, c["dim"]),
        f'<rect x="72" y="326" width="1136" height="226" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>',
        f'<line x1="72" y1="382" x2="1208" y2="382" stroke="{c["line"]}"/>',
    ]
    for i, colour in enumerate((c["cost"], c["base"], c["good"])):
        body.append(f'<circle cx="{104 + i * 30}" cy="354" r="9" fill="{colour}"/>')
    body.append(text(640, 364, "Claude Code", 26, c["dim"], family=MONO, text_anchor="middle"))
    for i, line in enumerate(INSTALL):
        y = 446 + i * 66
        body.append(text(104, y, "&gt;", 34, c["good"], family=MONO, font_weight="700"))
        body.append(text(146, y, line, 34, c["ink"], family=MONO))
    return svg(1280, 640, "spar-x-skills : des skills Claude Code prêtes pour la production", body, c["bg"])


def proof(c: dict[str, str], runs: int, multiple: float, saving: float) -> str:
    tiles = (
        (str(runs), c["ink"], ["exécutions valides,", "notées par tests ou oracle"]),
        (f"×{multiple:.1f}".replace(".", ","), c["cost"], ["coût d'Opus 5.5 en max", "face à high, sans gain"]),
        (f"−{saving:.0f} %", c["good"], ["de coût sur une recherche", "routée, mêmes réussites"]),
    )
    width, gap = 378, 25
    body = [text(48, 66, "Mesuré, pas promis", 40, c["ink"], font_weight="700")]
    for i, (value, tone, lines) in enumerate(tiles):
        x = 48 + i * (width + gap)
        body.append(
            f'<rect x="{x}" y="100" width="{width}" height="250" rx="14" '
            f'fill="{c["panel"]}" stroke="{c["line"]}"/>'
        )
        body.append(text(x + 28, 210, value, 84, tone, font_weight="700"))
        for j, line in enumerate(lines):
            body.append(text(x + 28, 268 + j * 36, line, 27, c["dim"]))
    return svg(1280, 390, "Résultats mesurés du benchmark rightsize", body, c["bg"])


def main() -> None:
    sweep = load("2026-10-31-effort-sweep.jsonl")
    cost: dict[str, list[float]] = defaultdict(list)
    for row in load("2026-10-30.jsonl"):
        if row["task"] == "t1-lookup":
            cost[row["label"]].append(row["cost_usd"])
    saving = (1 - mean(cost["routed"]) / mean(cost["baseline"])) * 100
    multiple = cost_index(sweep)["opus"]["max"]
    for theme, colours in THEMES.items():
        figures = {"cover": cover(colours), "proof": proof(colours, len(sweep), multiple, saving)}
        for name, content in figures.items():
            (OUT / f"{name}-{theme}.svg").write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
