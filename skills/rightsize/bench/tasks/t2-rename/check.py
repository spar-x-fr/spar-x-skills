import ast, pathlib, re, subprocess, sys
problems = []
tests = subprocess.run([sys.executable, "-m", "unittest", "-q"], capture_output=True, text=True)
if tests.returncode != 0:
    problems.append("tests fail")
for path in pathlib.Path(".").glob("*.py"):
    if re.search(r"\bcalc\b", path.read_text(encoding="utf-8")):
        problems.append(f"calc still in {path}")
tree = ast.parse(pathlib.Path("geometry.py").read_text(encoding="utf-8"))
fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "compute_area"), None)
if not fn or fn.returns is None or any(a.annotation is None for a in fn.args.args):
    problems.append("missing type hints")
print("pass" if not problems else "; ".join(problems)); sys.exit(1 if problems else 0)
