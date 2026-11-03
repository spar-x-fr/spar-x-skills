#!/usr/bin/env python3
"""The rightsize routing table as a pure function, so it can be tested and reused.

    python route.py --scope 1 --risk 1 --ambiguity 0 --depth 1
    python route.py --read --risk 0
    python route.py --depth 3 --risk 2 --json

The model scores the task (it understands the request far better than any keyword
list); this script only turns scores into a decision, the same way every time.
"""

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class Task:
    scope: int = 0
    risk: int = 0
    ambiguity: int = 0
    depth: int = 0
    tool_can_do_it: bool = False
    read_only: bool = False
    bulk: bool = False
    needs_history: bool = False
    tool_calls: int = 5
    failed_attempts: int = 0
    long_run: bool = False
    has_check: bool = False  # tests or an oracle will prove the result


@dataclass(frozen=True)
class Route:
    model: str
    effort: str
    mode: str
    plan_model: str = ""
    reason: str = ""


def validate(task: Task) -> Task:
    for name in ("scope", "risk", "ambiguity", "depth"):
        value = getattr(task, name)
        if not 0 <= value <= 3:
            raise ValueError(f"{name} doit être entre 0 et 3, reçu {value}")
    if task.tool_calls < 0 or task.failed_attempts < 0:
        raise ValueError("tool_calls et failed_attempts doivent être positifs")
    return task


def peak(task: Task) -> int:
    base = max(task.scope, task.ambiguity, task.depth)
    return min(3, base + (1 if task.risk >= 2 else 0))


def base_route(task: Task) -> Route:
    if task.tool_can_do_it:
        return Route("none", "none", "inline", reason="un outil déterministe suffit")
    if (task.read_only or task.bulk) and task.risk <= 1:
        return Route("haiku", "low", "", reason="lecture ou traitement en série, spec exacte")
    level = peak(task)
    if level <= 1:
        return Route("haiku", "low", "", reason="tâche simple")
    if level == 2:
        return Route("sonnet", "medium", "", reason="tâche standard")
    if task.depth == 3 and (task.risk >= 2 or task.long_run):
        return Route("opus", "xhigh", "", reason="raisonnement difficile à fort enjeu")
    if task.depth == 3 or task.risk == 3:
        return Route("opus", "high", "", reason="raisonnement difficile ou risque maximal")
    if max(task.scope, task.ambiguity) < 3:
        return Route("opus", "medium", "", reason="enjeu prod sur une tâche non triviale")
    return Route(
        "sonnet",
        "medium",
        "",
        plan_model="opus",
        reason="large ou ambigu : planifier avec opus, exécuter avec sonnet",
    )


# One rung per failure: effort first, then the next model. Fable and max only
# appear after opus at xhigh has failed.
LADDER = (
    ("none", "none"),
    ("haiku", "low"),
    ("haiku", "medium"),
    ("haiku", "high"),
    ("sonnet", "low"),
    ("sonnet", "medium"),
    ("sonnet", "high"),
    ("opus", "medium"),
    ("opus", "high"),
    ("opus", "xhigh"),
    ("fable", "xhigh"),
    ("fable", "max"),
)


def rung(model: str, effort: str) -> int:
    if (model, effort) in LADDER:
        return LADDER.index((model, effort))
    # Off-ladder starts (e.g. sonnet/low) enter at the first rung of their model.
    return next(i for i, (m, _) in enumerate(LADDER) if m == model)


def escalate(route: Route, failures: int) -> Route:
    if failures == 0:
        return route
    target = min(len(LADDER) - 1, rung(route.model, route.effort) + failures)
    model, effort = LADDER[target]
    if (model, effort) == (route.model, route.effort):
        return route
    return Route(
        model,
        effort,
        route.mode,
        route.plan_model,
        f"{route.reason} ; escaladé après {failures} échec(s)",
    )


STEP_DOWN = {"medium": "low", "high": "medium", "xhigh": "high"}


def verified_discount(task: Task, route: Route) -> Route:
    """With an automatic check, start one effort level lower: the check, not the
    effort, guarantees quality, and a failure escalates. Measured on 100 runs
    (bench/results/2026-10-31-effort-sweep.jsonl): every verified task passed from
    `low`, while xhigh cost 1.4-2.2x and max 3.7-9.3x of high. Never on R = 3."""
    if not task.has_check or task.risk == 3 or route.effort not in STEP_DOWN:
        return route
    return Route(
        route.model,
        STEP_DOWN[route.effort],
        route.mode,
        route.plan_model,
        f"{route.reason} ; un cran plus bas car vérifié automatiquement",
    )


def choose_mode(task: Task, route: Route) -> str:
    if route.model == "none":
        return "inline"
    if task.needs_history or task.tool_calls < 3:
        return "inline"
    if route.plan_model or (task.risk == 3 and task.scope >= 1):
        return "plan-then-subagents"
    return "subagent"


def route(task: Task) -> Route:
    task = validate(task)
    chosen = escalate(verified_discount(task, base_route(task)), task.failed_attempts)
    return Route(
        chosen.model, chosen.effort, choose_mode(task, chosen), chosen.plan_model, chosen.reason
    )


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("scope", "risk", "ambiguity", "depth"):
        parser.add_argument(f"--{name}", type=int, default=0, choices=range(4))
    parser.add_argument("--tool", dest="tool_can_do_it", action="store_true")
    parser.add_argument("--read", dest="read_only", action="store_true")
    parser.add_argument("--bulk", action="store_true")
    parser.add_argument("--history", dest="needs_history", action="store_true")
    parser.add_argument("--long", dest="long_run", action="store_true")
    parser.add_argument(
        "--checked",
        dest="has_check",
        action="store_true",
        help="tests or an oracle will verify the result",
    )
    parser.add_argument("--tool-calls", type=int, default=5)
    parser.add_argument("--failures", dest="failed_attempts", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = vars(parse_args(argv))
    as_json = args.pop("json")
    try:
        result = route(Task(**args))
    except ValueError as err:
        print(f"Entrée invalide : {err}", file=sys.stderr)
        return 2
    if as_json:
        print(json.dumps(asdict(result), ensure_ascii=False))
    else:
        plan = f" · plan : {result.plan_model}" if result.plan_model else ""
        print(f"{result.model} / {result.effort} · {result.mode}{plan} — {result.reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
