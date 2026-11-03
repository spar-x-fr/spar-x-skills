import unittest

from tinyre import search


class TinyReTest(unittest.TestCase):
    def test_basics(self):
        self.assertEqual(search("b+", "abbbc"), (1, 4))
        self.assertEqual(search("a.c", "xxabc"), (2, 5))
        self.assertIsNone(search("^b", "ab"))

    def test_lazy_and_backreference(self):
        self.assertEqual(search("a.*?c", "abcbc"), (0, 3))
        self.assertEqual(search(r"(a|b)\1", "abba"), (1, 3))


if __name__ == "__main__":
    unittest.main()
