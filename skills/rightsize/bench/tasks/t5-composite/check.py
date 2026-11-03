"""Grade the composite task with the three single-task checkers."""
import pathlib
import subprocess
import sys

answer, here = sys.argv[1], pathlib.Path(sys.argv[2])
tasks = here.parent
jobs = (
    ("t1-lookup", [answer]),
    ("t2-rename", []),
    ("t3-bugfix", [answer, str(here)]),  # this folder also holds hidden_test.py
)
results = []
for name, extra in jobs:
    run = subprocess.run([sys.executable, str(tasks / name / "check.py"), *extra],
                         capture_output=True, text=True)
    last = (run.stdout + run.stderr).strip().splitlines() or ["?"]
    results.append(f"{name}:{'ok' if run.returncode == 0 else last[-1][:80]}")
print(" | ".join(results))
sys.exit(0 if all(r.endswith(":ok") for r in results) else 1)
