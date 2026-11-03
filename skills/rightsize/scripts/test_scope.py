#!/usr/bin/env python3
"""Decide which tests a change needs, run only those, and remember full runs.

    python test_scope.py                 # plan: which tests, and why (JSON)
    python test_scope.py --run           # run the planned tests, record the result
    python test_scope.py --full --run    # end of sprint / before release: everything
    python test_scope.py --status        # last full run and recent scoped runs

When in doubt it runs more, never less. Rules, in order:
  1. --full, or no recorded green full run, or the last one is stale -> full suite.
  2. A shared file changed (lockfile, manifest, test config, CI) -> full suite.
  3. A changed file of a type it cannot map (yaml, sql, templates...) -> full suite.
  4. A changed source or test helper with no test mapped to it, even through its
     folder -> full suite.
  5. Otherwise: changed test files + tests named after or importing a changed file.
  6. Only docs or images changed -> nothing to run.

The ledger lives in .claude/rightsize/test-ledger.json inside the repository.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

LEDGER = Path(".claude") / "rightsize" / "test-ledger.json"
STALE_DAYS = 7
STALE_COMMITS = 30
SOURCE_EXT = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".vue",
    ".svelte",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".scala",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".dart",
    ".c",
    ".h",
    ".cc",
    ".cpp",
    ".hpp",
    ".ex",
    ".exs",
}
HARMLESS_EXT = {".md", ".rst", ".txt", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp"}
HARMLESS_NAMES = {
    "LICENSE",
    "LICENCE",
    "NOTICE",
    ".gitignore",
    ".gitattributes",
    ".editorconfig",
    "CODEOWNERS",
}
SHARED = re.compile(
    r"(^|/)(package(-lock)?\.json|pnpm-lock\.yaml|yarn\.lock|bun\.lockb?|poetry\.lock|"
    r"uv\.lock|Pipfile(\.lock)?|requirements[^/]*\.txt|pyproject\.toml|setup\.(py|cfg)|"
    r"tox\.ini|pytest\.ini|conftest\.py|go\.(mod|sum)|Cargo\.(toml|lock)|"
    r"Gemfile(\.lock)?|composer\.(json|lock)|pom\.xml|(build|settings)\.gradle(\.kts)?|"
    r"[^/]+\.(csproj|sln)|tsconfig[^/]*\.json|"
    r"(jest|vitest|vite|babel|webpack|playwright)\.config\.[^/]+|"
    r"\.github/workflows/[^/]+|\.nvmrc|\.python-version|Makefile|Dockerfile)$"
)
TEST_MODULE = re.compile(
    r"(^|/)(test_[^/]+\.py|[^/]+_test\.(py|go)|[^/]+\.(test|spec)\.[jt]sx?|"
    r"[^/]+Tests?\.(java|kt|cs)|[^/]+_spec\.rb)$"
)
TEST_DIR = re.compile(r"(^|/)(tests?|__tests__|spec)/")
IGNORED_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    "target",
    ".next",
    "coverage",
    ".claude",
}


@dataclass(frozen=True)
class Plan:
    mode: str  # full | scoped | none
    reason: str
    tests: list[str] = field(default_factory=list)
    unmapped: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    base: Optional[str] = None


# ---------------------------------------------------------------- git and files


def git(root: Optional[Path], *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "core.quotePath=false", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip() or f"git {' '.join(args)} a échoué")
    return done.stdout.strip()


def changed_files(root: Path, base: Optional[str]) -> list[str]:
    """Changed, deleted and untracked paths relative to the repository root.
    --no-renames keeps the old name of a moved file, whose tests still need to run."""
    tracked = git(root, "diff", "--name-only", "--no-renames", base or "HEAD", "--")
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "--full-name")
    names = {
        n.strip().replace("\\", "/") for n in (tracked + "\n" + untracked).splitlines() if n.strip()
    }
    ledger_dir = LEDGER.parent.as_posix() + "/"
    return sorted(n for n in names if not n.startswith(ledger_dir))


def all_test_files(root: Path) -> list[str]:
    found = []
    for path in root.rglob("*"):
        parts = path.relative_to(root).parts  # relative: a repo under build/ still counts
        if any(part in IGNORED_DIRS for part in parts):
            continue
        rel = "/".join(parts)
        if path.is_file() and path.suffix in SOURCE_EXT and TEST_MODULE.search(rel):
            found.append(rel)
    return sorted(found)


def is_test_module(path: str) -> bool:
    return bool(TEST_MODULE.search(path))


def is_code(path: str) -> bool:
    return Path(path).suffix in SOURCE_EXT


def is_harmless(path: str) -> bool:
    name = Path(path).name
    return Path(path).suffix.lower() in HARMLESS_EXT or name in HARMLESS_NAMES


# ---------------------------------------------------------------- impact mapping


def stem_of(path: str) -> str:
    stem = Path(path).stem
    return "" if stem in ("index", "__init__", "main", "mod", "lib") else stem


def references(test_text: str, stem: str) -> bool:
    """Does a test import or name the module? Word-bounded, so `user` is not `username`."""
    return bool(re.search(rf"(?<![\w-]){re.escape(stem)}(?![\w-])", test_text))


def tests_for(path: str, tests: list[str], texts: dict[str, str]) -> list[str]:
    stem = stem_of(path)
    if not stem:
        return []
    by_name = [t for t in tests if stem.lower() in Path(t).stem.lower()]
    by_import = [t for t in tests if references(texts[t], stem)]
    return sorted((set(by_name) | set(by_import)) - {path})


def folder_tests(path: str, tests: list[str]) -> list[str]:
    folder = Path(path).parent.as_posix()
    if folder in ("", "."):
        return []
    return [t for t in tests if t.startswith(folder + "/") or f"/{folder}/" in f"/{t}"]


# ---------------------------------------------------------------- ledger


def load_ledger(root: Path) -> dict[str, Any]:
    path = root / LEDGER
    if not path.exists():
        return {"last_full": None, "runs": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"last_full": None, "runs": []}
    except (OSError, json.JSONDecodeError) as err:
        print(f"[warn] registre illisible, ignoré : {err}", file=sys.stderr)
        return {"last_full": None, "runs": []}


def save_ledger(root: Path, ledger: dict[str, Any]) -> None:
    path = root / LEDGER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False), encoding="utf-8")


def stale_reason(root: Path, last_full: Optional[dict[str, Any]]) -> Optional[str]:
    if not isinstance(last_full, dict) or not last_full.get("passed"):
        return "aucune suite complète verte enregistrée"
    try:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(last_full["date"])
        behind = int(git(root, "rev-list", "--count", f"{last_full['commit']}..HEAD"))
    except (KeyError, TypeError, ValueError, RuntimeError):
        return "registre incomplet ou commit de la dernière suite complète introuvable"
    if age.days >= STALE_DAYS:
        return f"dernière suite complète il y a {age.days} jours"
    if behind >= STALE_COMMITS:
        return f"{behind} commits depuis la dernière suite complète"
    return None


# ---------------------------------------------------------------- planning


def make_plan(root: Path, force_full: bool, base: Optional[str]) -> Plan:
    last_full = load_ledger(root).get("last_full")
    if not base and isinstance(last_full, dict):
        base = last_full.get("commit")
    if force_full:
        return Plan(
            "full", "suite complète demandée (fin de sprint, release, commit final)", base=base
        )
    stale = stale_reason(root, last_full)
    if stale:
        return Plan("full", stale, base=base)
    changed = changed_files(root, base)
    relevant = [c for c in changed if not is_harmless(c)]
    if not relevant:
        return Plan(
            "none",
            "seuls des fichiers sans effet sur les tests ont changé"
            if changed
            else "rien n'a changé depuis la dernière suite verte",
            changed=changed,
            base=base,
        )

    def full(reason: str, unmapped: Iterable[str] = ()) -> Plan:
        return Plan("full", reason, unmapped=list(unmapped), changed=changed, base=base)

    shared = [c for c in relevant if SHARED.search(c)]
    if shared:
        return full(f"fichier partagé modifié : {', '.join(shared[:3])}")
    unknown = [c for c in relevant if not is_code(c)]
    if unknown:
        return full(f"type de fichier non classé, impact inconnu : {', '.join(unknown[:3])}")

    tests = all_test_files(root)
    texts = {t: (root / t).read_text(encoding="utf-8", errors="replace") for t in tests}
    selected = {c for c in relevant if is_test_module(c) and (root / c).exists()}
    unmapped = []
    for path in (c for c in relevant if not is_test_module(c)):  # sources and test helpers
        mapped = tests_for(path, tests, texts)
        if not mapped:
            unmapped.append(path)
            mapped = folder_tests(path, tests)
        if not mapped:
            return full(f"aucun test associé à {path} : impact inconnu", unmapped)
        selected.update(mapped)
    reason = f"{len(selected)} fichier(s) de test touché(s) par {len(relevant)} changement(s)"
    if unmapped:
        reason += f" ; sans test dédié, dossier testé : {', '.join(unmapped[:3])}"
    return Plan("scoped", reason, sorted(selected), unmapped, changed, base)


# ---------------------------------------------------------------- running


def language(test: str) -> str:
    suffix = Path(test).suffix
    return {".py": "python", ".go": "go", ".rs": "rust"}.get(
        suffix, "js" if re.search(r"\.[cm]?[jt]sx?$", test) else suffix
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def detect_command(root: Path, tests: list[str]) -> list[str]:
    """Best-effort runner for one language. Mixed languages need --cmd."""
    langs = {language(t) for t in tests}
    if len(langs) > 1:
        raise RuntimeError(
            f"tests en plusieurs langages ({', '.join(sorted(langs))}) : "
            "passez --cmd avec la commande qui les lance tous"
        )
    lang = langs.pop() if langs else None
    if lang == "python":
        uses_pytest = any(
            (root / n).exists() for n in ("pytest.ini", "conftest.py")
        ) or "pytest" in _read(root / "pyproject.toml")
        if uses_pytest:
            return [sys.executable, "-m", "pytest", "-q", *tests]
        return [sys.executable, "-m", "unittest", "-q", *(t[:-3].replace("/", ".") for t in tests)]
    if lang == "js":
        runner = "vitest" if "vitest" in _read(root / "package.json") else "jest"
        return ["npx", "vitest", "run", *tests] if runner == "vitest" else ["npx", "jest", *tests]
    if lang == "go":
        return ["go", "test", *sorted({"./" + Path(t).parent.as_posix() for t in tests})]
    if lang == "rust":
        return ["cargo", "test"]
    raise RuntimeError("lanceur de tests non reconnu : passez --cmd")


def expand_template(template: str, tests: list[str]) -> list[str]:
    """Split the template first, then insert the test paths as whole arguments."""
    tokens = shlex.split(template, posix=os.name != "nt")
    command = []
    for part in tokens:
        if part == "{tests}":
            command.extend(tests)
        else:
            command.append(part.replace("{tests}", " ".join(tests)))
    return command


def build_command(root: Path, plan: Plan, template: Optional[str]) -> list[str]:
    tests = all_test_files(root) if plan.mode == "full" else plan.tests
    if plan.mode == "full" and not tests and not template:
        raise RuntimeError("aucun fichier de test trouvé : une suite complète vide ne prouve rien")
    if template:
        return expand_template(template, [] if plan.mode == "full" else tests)
    return detect_command(root, tests)


def run_and_record(root: Path, plan: Plan, command: list[str], test_count: int) -> int:
    started = time.time()
    done = subprocess.run(
        command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    duration = round(time.time() - started, 1)
    passed = done.returncode == 0
    entry = {
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": _head(root),
        "mode": plan.mode,
        "passed": passed,
        "duration_s": duration,
        "tests": test_count,
        "command": " ".join(command),
    }
    ledger = load_ledger(root)
    runs = [*(ledger.get("runs") or [])[-19:], entry]
    last_full = entry if plan.mode == "full" else ledger.get("last_full")
    save_ledger(root, {**ledger, "last_full": last_full, "runs": runs})
    tail = (done.stdout + done.stderr).strip().splitlines()[-15:]
    print("\n".join(tail))
    print(f"\n[{plan.mode}] {'VERT' if passed else 'ROUGE'} en {duration} s")
    return done.returncode


def _head(root: Path) -> Optional[str]:
    try:
        return git(root, "rev-parse", "HEAD")
    except RuntimeError:
        return None


def main(argv: Optional[Sequence[str]] = None) -> int:
    for stream in (sys.stdout, sys.stderr):  # runners print ✓ and friends
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--full", action="store_true", help="force the whole suite")
    parser.add_argument("--base", help="git ref to diff against (default: last full run)")
    parser.add_argument("--run", action="store_true", help="run the planned tests and record")
    parser.add_argument("--cmd", help='runner template, e.g. "pytest -q {tests}"')
    parser.add_argument("--status", action="store_true", help="show the ledger")
    args = parser.parse_args(argv)
    try:
        root = Path(git(None, "rev-parse", "--show-toplevel"))
    except RuntimeError as err:
        print(f"Pas un dépôt git : {err}", file=sys.stderr)
        return 2
    if args.status:
        print(json.dumps(load_ledger(root), indent=2, ensure_ascii=False))
        return 0
    try:
        plan = make_plan(root, args.full, args.base)
        command = build_command(root, plan, args.cmd) if plan.mode != "none" else []
    except RuntimeError as err:
        print(f"Erreur : {err}", file=sys.stderr)
        return 2
    count = len(all_test_files(root)) if plan.mode == "full" else len(plan.tests)
    print(json.dumps({**asdict(plan), "command": " ".join(command)}, indent=2, ensure_ascii=False))
    if args.run and plan.mode != "none":
        return run_and_record(root, plan, command, count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
