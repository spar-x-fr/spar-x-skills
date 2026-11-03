import unittest

from routes import cheapest_tour


class RoutesTest(unittest.TestCase):
    def test_simple(self):
        roads = [(0, 1, 2, False), (1, 2, 2, False), (0, 2, 1, True)]
        self.assertEqual(cheapest_tour(3, roads, 0, [2], 0), 8)
        self.assertEqual(cheapest_tour(3, roads, 0, [2], 2), 2)

    def test_unreachable(self):
        self.assertEqual(cheapest_tour(3, [(0, 1, 1, False)], 0, [2], 3), -1)


if __name__ == "__main__":
    unittest.main()
