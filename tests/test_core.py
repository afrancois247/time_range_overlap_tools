import unittest
from datetime import datetime, timedelta

from time_range_overlap_tools import Range, intersect, union, total_covered_seconds


def dt(h: int, m: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m)


class TestRangeConstruction(unittest.TestCase):
    def test_inverted_raises(self):
        with self.assertRaises(ValueError):
            Range(dt(10), dt(9))

    def test_zero_length_allowed(self):
        r = Range(dt(9), dt(9))
        self.assertEqual(r.duration, timedelta(0))


class TestOverlapPredicate(unittest.TestCase):
    def test_overlapping(self):
        a = Range(dt(9), dt(11))
        b = Range(dt(10), dt(12))
        self.assertTrue(a.overlaps(b))

    def test_touching_not_overlapping(self):
        a = Range(dt(9), dt(10))
        b = Range(dt(10), dt(11))
        self.assertFalse(a.overlaps(b))

    def test_disjoint(self):
        a = Range(dt(9), dt(10))
        b = Range(dt(11), dt(12))
        self.assertFalse(a.overlaps(b))


class TestUnion(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(union([]), [])

    def test_single(self):
        r = Range(dt(9), dt(10))
        self.assertEqual(union([r]), [r])

    def test_disjoint_returned_sorted(self):
        a = Range(dt(11), dt(12))
        b = Range(dt(9), dt(10))
        self.assertEqual(union([a, b]), [b, a])

    def test_overlapping_merged(self):
        a = Range(dt(9), dt(11))
        b = Range(dt(10), dt(12))
        self.assertEqual(union([a, b]), [Range(dt(9), dt(12))])

    def test_contained_swallowed(self):
        a = Range(dt(9), dt(12))
        b = Range(dt(10), dt(11))
        self.assertEqual(union([a, b]), [a])

    def test_touching_not_merged(self):
        a = Range(dt(9), dt(10))
        b = Range(dt(10), dt(11))
        self.assertEqual(union([a, b]), [a, b])

    def test_zero_length_dropped(self):
        a = Range(dt(9), dt(9))
        b = Range(dt(10), dt(11))
        self.assertEqual(union([a, b]), [b])


class TestIntersect(unittest.TestCase):
    def test_empty_returns_none(self):
        self.assertIsNone(intersect([]))

    def test_single(self):
        r = Range(dt(9), dt(10))
        self.assertEqual(intersect([r]), r)

    def test_pair_overlap(self):
        a = Range(dt(9), dt(11))
        b = Range(dt(10), dt(12))
        self.assertEqual(intersect([a, b]), Range(dt(10), dt(11)))

    def test_pair_touching_returns_none(self):
        a = Range(dt(9), dt(10))
        b = Range(dt(10), dt(11))
        self.assertIsNone(intersect([a, b]))

    def test_disjoint_returns_none(self):
        a = Range(dt(9), dt(10))
        b = Range(dt(11), dt(12))
        self.assertIsNone(intersect([a, b]))

    def test_three_with_common_core(self):
        a = Range(dt(9), dt(12))
        b = Range(dt(10), dt(13))
        c = Range(dt(11), dt(14))
        self.assertEqual(intersect([a, b, c]), Range(dt(11), dt(12)))


class TestTotalCoveredSeconds(unittest.TestCase):
    def test_disjoint_summed(self):
        ranges = [Range(dt(9), dt(10)), Range(dt(11), dt(12))]
        self.assertEqual(total_covered_seconds(ranges), 7200.0)

    def test_overlap_counted_once(self):
        ranges = [Range(dt(9), dt(11)), Range(dt(10), dt(12))]
        self.assertEqual(total_covered_seconds(ranges), 10800.0)

    def test_empty(self):
        self.assertEqual(total_covered_seconds([]), 0.0)


if __name__ == "__main__":
    unittest.main()
