import unittest

from scheduler import schedule


class SchedulerTest(unittest.TestCase):
    def test_precedence_beats_deadline_order(self):
        jobs = {"a": (3, 10), "b": (1, 2), "c": (2, 4)}
        order = schedule(jobs, [("a", "b")])
        self.assertLess(order.index("a"), order.index("b"))
        self.assertEqual(sorted(order), ["a", "b", "c"])

    def test_cycle(self):
        with self.assertRaises(ValueError):
            schedule({"a": (1, 1), "b": (1, 1)}, [("a", "b"), ("b", "a")])


if __name__ == "__main__":
    unittest.main()
