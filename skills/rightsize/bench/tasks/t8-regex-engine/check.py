import ast, pathlib, random, re, sys, signal, threading
sys.path.insert(0, ".")
source = pathlib.Path("tinyre.py").read_text(encoding="utf-8")
banned = {"re", "sre_compile", "sre_parse", "sre_constants", "regex", "fnmatch", "_sre"}
for node in ast.walk(ast.parse(source)):
    names = []
    if isinstance(node, ast.Import):
        names = [a.name.split(".")[0] for a in node.names]
    elif isinstance(node, ast.ImportFrom) and node.module:
        names = [node.module.split(".")[0]]
    elif isinstance(node, ast.Call) and getattr(node.func, "id", "") == "__import__":
        names = ["__import__"]
    if banned & set(names) or "__import__" in names or "importlib" in names:
        print("uses a regex library"); sys.exit(1)
from tinyre import search

ATOMS = ["a", "b", "c", ".", "[ab]", "[^a]", "[a-b]", r"\.", "x"]


def gen(rng, depth=0):
    parts = []
    for _ in range(rng.randint(1, 3)):
        r = rng.random()
        if r < 0.55 or depth > 2:
            piece = rng.choice(ATOMS)
        elif r < 0.75:
            piece = "(" + gen(rng, depth + 1) + ")"
        elif r < 0.85:
            piece = "(?:" + gen(rng, depth + 1) + ")"
        else:
            piece = "(" + gen(rng, depth + 1) + "|" + gen(rng, depth + 1) + ")"
        if rng.random() < 0.45:
            piece += rng.choice(["*", "+", "?", "{2}", "{1,2}", "{0,}", "*?", "+?", "??", "{1,3}?"])
        parts.append(piece)
    return "".join(parts)


def capturing(pattern):
    return pattern.count("(") - pattern.count("(?:") - pattern.count(r"\(")


def with_extras(rng, pattern):
    # Backreferences only target a top-level, unrepeated group: the captures of
    # groups inside repetitions follow CPython implementation quirks, not a spec.
    if rng.random() < 0.35:
        target = "(" + gen(rng, 2) + ")"
        number = capturing(pattern) + 1
        tail = gen(rng, 2) if rng.random() < 0.5 else ""
        pattern = pattern + target + tail + "\\" + str(number) if number <= 9 else pattern
    if rng.random() < 0.15:
        pattern = "^" + pattern
    if rng.random() < 0.15:
        pattern += "$"
    return pattern


rng = random.Random(2026)
checked = 0
while checked < 3000:
    pattern = with_extras(rng, gen(rng))
    try:
        compiled = re.compile(pattern)
    except re.error:
        continue
    text = "".join(rng.choice("abcx.") for _ in range(rng.randint(0, 9)))
    m = compiled.search(text)
    expected = m.span() if m else None
    try:
        got = search(pattern, text)
    except Exception as err:
        print(f"crash on {pattern!r} / {text!r}: {err!r}"[:200]); sys.exit(1)
    if got != expected:
        print(f"wrong on {pattern!r} / {text!r}: got {got}, expected {expected}"[:200]); sys.exit(1)
    checked += 1
for bad in ["(", "a)", "[ab", "*a", "a{2,1}"]:
    try:
        search(bad, "a")
    except ValueError:
        continue
    print(f"no ValueError for {bad!r}"); sys.exit(1)
print("pass")
