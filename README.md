# time_range_overlap_tools

Computes the intersection and union of multiple datetime ranges using half-open intervals (inclusive start, exclusive end).

## Usage

```python
from datetime import datetime
from time_range_overlap_tools import Range, intersect, union, total_covered_seconds

a = Range(datetime(2024, 1, 1, 9), datetime(2024, 1, 1, 11))
b = Range(datetime(2024, 1, 1, 10), datetime(2024, 1, 1, 12))

print(intersect([a, b]))        # Range(2024-01-01 10:00, 2024-01-01 11:00)
print(union([a, b]))            # [Range(2024-01-01 09:00, 2024-01-01 12:00)]
print(total_covered_seconds([a, b]))  # 10800.0
```

## Why

Calendar and scheduling problems are full of range arithmetic. The two operations that come up over and over — "what time is free for *everyone*" (intersection) and "what is the total span covered by these blocks" (union) — are trivial to get wrong when intervals touch. This library exists to get those two things right in a way that composes.

The core trade-off is half-open semantics. A 09:00–10:00 block and a 10:00–11:00 block do **not** overlap: they share no instant. This matches how calendar tools think but differs from closed-interval math where `[9, 10]` and `[10, 11]` intersect at the single point `10`. Half-open also means `range.start == range.end` defines an empty range, which this library silently drops.

## Edge cases

- **Touching ranges are not merged by `union`.** `[09:00–10:00]` and `[10:00–11:00]` produce two ranges, not one `09:00–11:00`.
- **Touching ranges yield no intersection.** `intersect` returns `None` when any pair only touches.
- **Zero-length ranges are dropped** everywhere; they contain no instants and cannot contribute.
- **`intersect` of an empty iterable returns `None`.**
- **`union` never merges by containment alone;** a range fully inside another is swallowed.

## Exported names

- `Range(start, end)` — a half-open `[start, end)` interval with `.duration`, `.overlaps(other)`, and `.intersect(other)`.
- `union(ranges)` — merge a list of `Range` objects into the minimal disjoint list.
- `intersect(ranges)` — the single `Range` common to all inputs, or `None`.
- `total_covered_seconds(ranges)` — wall-clock seconds covered by the union.

Standard library only. Tested with `PYTHONPATH=src python -m unittest discover -s tests`.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Limitations

Values are coerced to floats, so very large integers lose precision. If you need
exact integer aggregates over a window, this is the wrong tool.

## Contributing

Issues and pull requests are welcome. Please keep the dependency list empty —
that constraint is the point of the project, not an oversight.

