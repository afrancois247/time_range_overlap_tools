from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, List, Optional, Tuple


@dataclass(frozen=True)
class Range:
    """An inclusive-start, exclusive-end half-open interval over datetimes.

    Half-open semantics are used so that two adjacent ranges A and B where
    ``A.end == B.start`` do *not* overlap — touching is distinct from
    intersecting. This matches how calendar scheduling tools usually think:
    a 09:00–10:00 block and a 10:00–11:00 block do not conflict.
    """

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.start > self.end:
            raise ValueError(
                f"Range start ({self.start}) must be <= end ({self.end})"
            )

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def overlaps(self, other: "Range") -> bool:
        return self.start < other.end and other.start < self.end

    def intersect(self, other: "Range") -> Optional["Range"]:
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        if start < end:
            return Range(start, end)
        return None


def _normalize(ranges: Iterable[Range]) -> List[Range]:
    """Drop zero-length ranges and return a sorted copy.

    A zero-length range (start == end) contains no instants, so it can never
    contribute to an intersection or union. Filtering them early keeps the
    merge logic clean.
    """
    kept = [r for r in ranges if r.start < r.end]
    kept.sort(key=lambda r: (r.start, r.end))
    return kept


def union(ranges: Iterable[Range]) -> List[Range]:
    """Merge possibly-overlapping ranges into a minimal disjoint list.

    Returns ranges sorted by start time. Touching ranges (``a.end == b.start``)
    are *not* merged — they remain separate — because half-open intervals that
    touch share no instants.
    """
    clean = _normalize(ranges)
    if not clean:
        return []
    result: List[Range] = [clean[0]]
    for r in clean[1:]:
        last = result[-1]
        if r.start < last.end:  # overlap only; touching is not merged
            # Only extend when r actually reaches past last.end; otherwise
            # r is fully swallowed by last and we drop it silently.
            if r.end > last.end:
                result[-1] = Range(last.start, r.end)
        else:
            result.append(r)
    return result


def intersect(ranges: Iterable[Range]) -> Optional[Range]:
    """Compute the single intersection of all ranges.

    Returns ``None`` when any pair fails to overlap (half-open: touching is
    not overlapping). The intersection of N ranges is itself a single range
    or empty — it can never be a disjoint list.
    """
    clean = _normalize(ranges)
    if not clean:
        return None
    cur = clean[0]
    for r in clean[1:]:
        cur = cur.intersect(r)
        if cur is None:
            return None
    return cur


def total_covered_seconds(ranges: Iterable[Range]) -> float:
    """Sum the wall-clock seconds covered by the union of ranges.

    Overlaps are counted once because the ranges are unioned first.
    """
    return sum(r.duration.total_seconds() for r in union(ranges))
