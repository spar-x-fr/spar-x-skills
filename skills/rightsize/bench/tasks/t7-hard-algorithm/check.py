import heapq, random, sys, time
sys.path.insert(0, ".")
from routes import cheapest_tour


def exhaustive(n, roads, depot, stops, max_tolls):
    """Reference: Dijkstra over (junction, visited stops, tolls used), written for clarity."""
    targets = sorted(set(stops))
    index = {s: i for i, s in enumerate(targets)}
    full = (1 << len(targets)) - 1
    adj = [[] for _ in range(n)]
    for a, b, c, t in roads:
        adj[a].append((b, c, t)); adj[b].append((a, c, t))
    start_mask = (1 << index[depot]) if depot in index else 0
    best = {(depot, start_mask, 0): 0}
    heap = [(0, depot, start_mask, 0)]
    while heap:
        d, u, m, k = heapq.heappop(heap)
        if best.get((u, m, k), 1 << 60) < d:
            continue
        if u == depot and m == full:
            return d
        for v, c, t in adj[u]:
            nk = k + (1 if t else 0)
            if nk > max_tolls:
                continue
            nm = m | (1 << index[v]) if v in index else m
            if d + c < best.get((v, nm, nk), 1 << 60):
                best[(v, nm, nk)] = d + c
                heapq.heappush(heap, (d + c, v, nm, nk))
    return -1


def brute(n, roads, depot, stops, max_tolls):
    """Independent check: Bellman-Ford over (junction, tolls), then every order of the stops."""
    from itertools import permutations
    INF = float("inf")
    targets = sorted(set(stops) - {depot})
    if not targets:
        return 0
    def leg(s):
        dist = [[INF] * (max_tolls + 1) for _ in range(n)]
        dist[s][0] = 0
        for _ in range(n * (max_tolls + 1)):
            changed = False
            for a, b, c, t in roads:
                for u, v in ((a, b), (b, a)):
                    for k in range(max_tolls + 1):
                        nk = k + (1 if t else 0)
                        if nk <= max_tolls and dist[u][k] + c < dist[v][nk]:
                            dist[v][nk] = dist[u][k] + c
                            changed = True
            if not changed:
                break
        return dist
    legs = {s: leg(s) for s in [depot] + targets}
    best = INF
    for order in permutations(targets):
        path = [depot, *order, depot]
        budget = {0: 0}  # tolls used -> min cost so far
        for x, y in zip(path, path[1:]):
            nxt = {}
            for used, cost in budget.items():
                for k in range(max_tolls - used + 1):
                    d = legs[x][y][k]
                    if d < INF and cost + d < nxt.get(used + k, INF):
                        nxt[used + k] = cost + d
            budget = nxt
        if budget:
            best = min(best, min(budget.values()))
    return -1 if best == INF else best


def instance(rng, n, m, stops, tolls):
    roads = []
    for _ in range(m):
        a, b = rng.randrange(n), rng.randrange(n)
        if a != b:
            roads.append((a, b, rng.randint(1, 9), rng.random() < 0.35))
    return n, roads, rng.randrange(n), [rng.randrange(n) for _ in range(stops)], tolls


rng = random.Random(11)
for case in range(250):
    args = instance(rng, rng.randint(2, 6), rng.randint(1, 9), rng.randint(0, 3), rng.randint(0, 2))
    expected = exhaustive(*args)
    if case < 60:  # cross-check the reference itself on the tiniest cases
        assert expected == brute(*args), ("reference mismatch", args)
    got = cheapest_tour(*args)
    if got != expected:
        print(f"wrong on case {case}: got {got}, expected {expected}"); sys.exit(1)
args = instance(random.Random(5), 200, 1000, 8, 4)
start = time.perf_counter(); got = cheapest_tour(*args); took = time.perf_counter() - start
if got != exhaustive(*args) or took > 2.0:
    print(f"large case wrong or slow ({took:.2f}s)"); sys.exit(1)
print("pass")
