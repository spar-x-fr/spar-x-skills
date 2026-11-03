import itertools, random, sys, time
sys.path.insert(0, ".")
from scheduler import schedule


def lmax(order, jobs):
    t, worst = 0, None
    for name in order:
        t += jobs[name][0]
        late = t - jobs[name][1]
        worst = late if worst is None else max(worst, late)
    return worst


def valid(order, jobs, before):
    pos = {n: i for i, n in enumerate(order)}
    return sorted(order) == sorted(jobs) and all(pos[a] < pos[b] for a, b in before)


def best(jobs, before):
    return min(lmax(p, jobs) for p in itertools.permutations(jobs) if valid(p, jobs, before))


def instance(rng, n):
    names = [f"j{i}" for i in range(n)]
    jobs = {x: (rng.randint(1, 9), rng.randint(1, 30)) for x in names}
    before = [(names[i], names[j]) for i in range(n) for j in range(i + 1, n) if rng.random() < 0.25]
    rng.shuffle(names)
    return {x: jobs[x] for x in names}, before


rng = random.Random(7)
for case in range(150):
    jobs, before = instance(rng, rng.randint(2, 7))
    order = schedule(jobs, before)
    if not valid(order, jobs, before) or lmax(order, jobs) != best(jobs, before):
        print(f"wrong on case {case}"); sys.exit(1)
jobs, before = instance(random.Random(1), 300)
start = time.perf_counter(); order = schedule(jobs, before); took = time.perf_counter() - start
if not valid(order, jobs, before) or took > 2:
    print(f"large case invalid or slow ({took:.2f}s)"); sys.exit(1)
try:
    schedule({"a": (1, 1), "b": (1, 1), "c": (1, 1)}, [("a", "b"), ("b", "c"), ("c", "a")])
    print("cycle not detected"); sys.exit(1)
except ValueError:
    pass
print("pass")
