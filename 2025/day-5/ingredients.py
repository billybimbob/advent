#! /usr/bin/env python3

from typing import NamedTuple
from argparse import ArgumentParser
import re


class FreshRange(NamedTuple):
    start: int
    end: int

    def in_range(self, ingredient: int) -> bool:
        return self.start <= ingredient <= self.end


def total_possible_fresh(fresh_ranges: list[FreshRange]) -> int:
    ranges_by_start = sorted(fresh_ranges, key=lambda r: r.start)
    dedupe_ranges = list[FreshRange]()

    for fresh_range in ranges_by_start:
        prior_range = dedupe_ranges[-1] if dedupe_ranges else None

        if not prior_range:
            dedupe_ranges.append(fresh_range)
            continue

        start, end = fresh_range

        if not prior_range.in_range(start) and prior_range.start < start:
            dedupe_ranges.append(fresh_range)
            continue

        if not prior_range.in_range(end):
            dedupe_ranges.append(FreshRange(prior_range.end + 1, end))
            continue

    return sum(f.end - f.start + 1 for f in dedupe_ranges if f.start <= f.end)


def count_fresh_ingredients(ingredients_file: str, total_fresh: bool) -> int:
    fresh_count = 0

    with open(ingredients_file, "r") as f:
        fresh_ranges = list[FreshRange]()
        is_checking_freshness = False

        for line in f:
            if not line.strip():
                is_checking_freshness = True
                continue

            if not is_checking_freshness:
                match = re.match(r"^(\d+)-(\d+)$", line)
                if match:
                    new_range = FreshRange(int(match.group(1)), int(match.group(2)))
                    fresh_ranges.append(new_range)
                continue

            ingredient = int(line.strip())
            if any(f.in_range(ingredient) for f in fresh_ranges):
                fresh_count += 1

    if total_fresh:
        return total_possible_fresh(fresh_ranges)

    return fresh_count


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("ingredients_file")
    parser.add_argument("-t", "--total", action="store_true", dest="total_fresh")
    args = parser.parse_args()

    fresh_count = count_fresh_ingredients(args.ingredients_file, args.total_fresh)
    print(fresh_count)
