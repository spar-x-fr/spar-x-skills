import unittest

from durations import parse_duration


class DurationTest(unittest.TestCase):
    def test_hours_minutes(self):
        self.assertEqual(parse_duration("1h30m"), 5400)

    def test_seconds(self):
        self.assertEqual(parse_duration("45s"), 45)

    def test_spaces(self):
        self.assertEqual(parse_duration("2h 5m 10s"), 7510)


if __name__ == "__main__":
    unittest.main()
