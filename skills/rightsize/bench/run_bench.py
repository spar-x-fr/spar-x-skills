#!/usr/bin/env python3
"""Run a benchmark task headless with a given model/effort and grade it.

    python run_bench.py --task t3-bugfix --model sonnet --effort medium --label routed
    python run_bench.py --task t5-composite --model opus --effort high --with-skill

Each run copies tasks/<task>/repo into a fresh folder, runs `claude -p` there,
grades the result with tasks/<task>/check.py and appends one JSON line to the
results file. Every run spends real tokens: keep --reps small.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Optional

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILL = ROOT
TOOLS = "Read Edit Write Glob Grep Bash(python *) Bash(ls *) Bash(cat *)"


def parse_args(argv: Optional[list[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--task", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True)
    parser.add_argument("--label", default="run")
    parser.add_argument("--reps", type=int, default=1)
    parser.add_argument(
        "--with-skill",
        action="store_true",
        help="install the rightsize skill and agents in the run folder",
    )
    parser.add_argument(
        "--workdir",
        default=str(Path.home() / "rs-bench"),
        help="keep it short on Windows (260-character path limit)",
    )
    parser.add_argument("--out", default=str(HERE / "results.jsonl"))
    parser.add_argument("--claude", default="claude", help="path to the claude executable")
    parser.add_argument("--budget", type=float, default=3.0, help="max USD per run")
    parser.add_argument("--timeout", type=int, default=900)
    return parser.parse_args(argv)


def prepare(task_dir: Path, run_dir: Path, with_skill: bool) -> None:
    if run_dir.exists():
        shutil.rmtree(run_dir)
    shutil.copytree(task_dir / "repo", run_dir)
    if with_skill:
        target = run_dir / ".claude"
        shutil.copytree(
            SKILL,
            target / "skills" / "rightsize",
            ignore=shutil.ignore_patterns(
                "__pycache__",
                "*.bak",
                ".*",
                "agents",
                "bench",
                "docs",
                "examples",
                "hooks",
                "tests",
            ),
        )
        shutil.copytree(ROOT / "agents", target / "agents")


def run_claude(args: argparse.Namespace, prompt: str, run_dir: Path) -> dict[str, Any]:
    tools = TOOLS + (" Agent Skill" if args.with_skill else "")
    command = [
        args.claude,
        "-p",
        prompt,
        "--model",
        args.model,
        "--effort",
        args.effort,
        "--output-format",
        "json",
        "--setting-sources",
        "project",
        "--no-session-persistence",
        "--max-budget-usd",
        str(args.budget),
        "--allowedTools",
        tools,
    ]
    started = time.time()
    try:
        done = subprocess.run(
            command,
            cwd=run_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=args.timeout,
            stdin=subprocess.DEVNULL,
        )  # else claude waits 3 s for stdin
    except subprocess.TimeoutExpired:
        return {"is_error": True, "result": "timeout", "wall_s": args.timeout}
    data: dict[str, Any]
    try:
        data = json.loads(done.stdout)
    except json.JSONDecodeError:
        data = {"is_error": True, "result": (done.stdout + done.stderr)[-2000:]}
    data["wall_s"] = round(time.time() - started, 1)
    return data


INFRA_MARKERS = (
    "credit balance is too low",
    "usage limit",
    "rate limit",
    "overloaded",
    "authentication",
    "please run /login",
)


def infra_error(data: dict[str, Any]) -> bool:
    """True when the run says nothing about the model: the account or the service
    refused it (no credit, usage limit, outage). Such runs are excluded from results."""
    text = str(data.get("result", "")).lower()
    return bool(data.get("is_error")) and (
        any(m in text for m in INFRA_MARKERS) or (data.get("num_turns") or 0) <= 1
    )


def grade(task_dir: Path, run_dir: Path, answer: str) -> tuple[bool, str]:
    answer_file = run_dir / "_answer.txt"
    answer_file.write_text(answer or "", encoding="utf-8")
    try:
        check = subprocess.run(
            [sys.executable, str(task_dir / "check.py"), str(answer_file), str(task_dir)],
            cwd=run_dir,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:  # e.g. a regex engine looping on (a*)*
        return False, "check timed out after 300 s"
    detail = (check.stdout + check.stderr).strip().splitlines()
    return check.returncode == 0, (detail[-1] if detail else "")


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    task_dir = HERE / "tasks" / args.task
    if not (task_dir / "prompt.txt").exists():
        print(f"Tâche inconnue : {task_dir}", file=sys.stderr)
        return 2
    prompt = (task_dir / "prompt.txt").read_text(encoding="utf-8").strip()
    for rep in range(1, args.reps + 1):
        name = f"{args.label}-{args.task}-{args.model}-{args.effort}-{rep}"
        run_dir = Path(args.workdir) / name
        prepare(task_dir, run_dir, args.with_skill)
        data = run_claude(args, prompt, run_dir)
        if infra_error(data):
            print(
                f"{name}: ARRÊT, erreur d'infrastructure, rien n'est enregistré : "
                f"{str(data.get('result', ''))[:120]}",
                file=sys.stderr,
            )
            return 3
        passed, detail = grade(task_dir, run_dir, data.get("result", ""))
        row = {
            "label": args.label,
            "task": args.task,
            "model": args.model,
            "effort": args.effort,
            "with_skill": args.with_skill,
            "rep": rep,
            "passed": passed,
            "check": detail,
            "cost_usd": data.get("total_cost_usd"),
            "turns": data.get("num_turns"),
            "wall_s": data.get("wall_s"),
            "is_error": data.get("is_error"),
            "usage": data.get("usage"),
            "model_usage": data.get("modelUsage"),
        }
        with Path(args.out).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        cost = row["cost_usd"] if row["cost_usd"] is not None else float("nan")
        print(
            f"{name}: {'PASS' if passed else 'FAIL'} ({detail}) {cost:.4f} $ "
            f"{row['turns']} tours {row['wall_s']} s"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
