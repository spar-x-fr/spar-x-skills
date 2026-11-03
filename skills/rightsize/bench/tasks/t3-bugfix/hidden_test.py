import unittest
from durations import parse_duration


class Hidden(unittest.TestCase):
    def test_valid(self):
        for text, expected in [("1h30m", 5400), ("45s", 45), ("2h 5m 10s", 7510),
                               ("10m", 600), ("0s", 0), ("12h", 43200), (" 3m ", 180)]:
            self.assertEqual(parse_duration(text), expected, text)

    def test_invalid(self):
        for text in ["5x", "h", "10", "3m4", "m5s"]:
            with self.assertRaises(ValueError, msg=text):
                parse_duration(text)
