import random
import unittest
from collections import OrderedDict

from ttl_cache import TTLCache


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class Model:
    """Straightforward reference implementation of the docstring."""

    def __init__(self, capacity, clock):
        self.capacity, self.clock, self.data = capacity, clock, OrderedDict()

    def alive(self, entry):
        return entry[2] is None or self.clock() < entry[2]

    def purge(self):
        for key in [k for k, e in self.data.items() if not self.alive(e)]:
            del self.data[key]

    def put(self, key, value, weight=1, ttl=None):
        self.data.pop(key, None)
        if weight > self.capacity:
            return
        self.data[key] = (value, weight, None if ttl is None else self.clock() + ttl)
        self.purge()
        while sum(e[1] for e in self.data.values()) > self.capacity:
            self.data.popitem(last=False)

    def get(self, key, default=None):
        entry = self.data.get(key)
        if entry is None or not self.alive(entry):
            return default
        self.data.move_to_end(key)
        return entry[0]

    def live(self):
        return [e for e in self.data.values() if self.alive(e)]


class Hidden(unittest.TestCase):
    def test_ttl_boundary(self):
        clock = Clock()
        cache = TTLCache(5, clock=clock)
        cache.put("a", 1, ttl=10)
        clock.now = 9.999
        self.assertEqual(cache.get("a"), 1)
        clock.now = 10.0
        self.assertIsNone(cache.get("a"))
        self.assertEqual((len(cache), cache.weight), (0, 0))

    def test_random_against_reference(self):
        for seed in range(300):
            rng = random.Random(seed)
            clock_a, clock_b = Clock(), Clock()
            capacity = rng.randint(1, 8)
            real, model = TTLCache(capacity, clock=clock_a), Model(capacity, clock_b)
            for step in range(60):
                op = rng.random()
                key = rng.choice("abcdef")
                if op < 0.45:
                    weight = rng.randint(1, 5)
                    ttl = rng.choice([None, 1, 2, 3, 5])
                    real.put(key, step, weight, ttl)
                    model.put(key, step, weight, ttl)
                elif op < 0.85:
                    self.assertEqual(real.get(key), model.get(key), f"seed {seed} step {step} get {key}")
                else:
                    advance = rng.choice([0.5, 1, 2])
                    clock_a.now += advance
                    clock_b.now += advance
                live = model.live()
                self.assertEqual(len(real), len(live), f"seed {seed} step {step} len")
                self.assertEqual(real.weight, sum(e[1] for e in live), f"seed {seed} step {step} weight")
