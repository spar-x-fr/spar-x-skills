import math
import unittest

import geometry
import invoice
import report


class GeometryTest(unittest.TestCase):
    def test_areas(self):
        self.assertAlmostEqual(geometry.compute_area("circle", 1), math.pi)
        self.assertEqual(geometry.compute_area("rect", 2, 3), 6)
        self.assertEqual(geometry.compute_area("triangle", 2, 3), 3)

    def test_callers(self):
        self.assertEqual(invoice.floor_price(2, 3), 75.0)
        self.assertEqual(report.summary([("rect", 1, 2)]), "1 shapes, total area 2.00")


if __name__ == "__main__":
    unittest.main()
