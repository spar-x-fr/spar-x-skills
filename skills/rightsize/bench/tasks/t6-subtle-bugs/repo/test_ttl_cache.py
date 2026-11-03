import unittest

from ttl_cache import TTLCache


class Clock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class TTLCacheTest(unittest.TestCase):
    def test_basic(self):
        cache = TTLCache(3, clock=Clock())
        cache.put("a", 1)
        self.assertEqual(cache.get("a"), 1)
        self.assertIsNone(cache.get("missing"))


if __name__ == "__main__":
    unittest.main()
