#! /usr/bin/env python3

from argparse import ArgumentParser
from collections import Counter
from collections.abc import Iterable
from typing import NamedTuple

ROLL_SPOT = "@"


class Coordinate(NamedTuple):
    x: int
    y: int


def count_accessible_rolls(rolls_map_path) -> int:
    with open(rolls_map_path, "r") as f:
        max_x, max_y = 0, 0
        roll_counts = Counter[Coordinate]()
        roll_spots = set[Coordinate]()

        for y, line in enumerate(f):
            max_x = max(max_x, len(line))

            if line:
                max_y += 1

            for x, spot in enumerate(line):
                if spot != ROLL_SPOT:
                    continue

                for adj_pos in adjacent_positions(x, y):
                    roll_counts[adj_pos] += 1

                roll_spots.add(Coordinate(x, y))

        accessible_rolls = 0
        can_remove = True

        while can_remove:
            grabbed_rolls = list[Coordinate]()
            can_remove = False

            for pos in roll_spots:
                count = roll_counts[pos]
                if count >= 4:
                    continue

                for adj_pos in adjacent_positions(pos.x, pos.y):
                    roll_counts[adj_pos] -= 1

                grabbed_rolls.append(pos)
                accessible_rolls += 1
                can_remove = True

            roll_spots.difference_update(grabbed_rolls)

        return accessible_rolls


def adjacent_positions(x: int, y: int) -> Iterable[Coordinate]:
    yield Coordinate(x, y - 1)
    yield Coordinate(x, y + 1)

    yield Coordinate(x - 1, y)
    yield Coordinate(x - 1, y - 1)
    yield Coordinate(x - 1, y + 1)

    yield Coordinate(x + 1, y)
    yield Coordinate(x + 1, y - 1)
    yield Coordinate(x + 1, y + 1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("rolls_map_path")
    # parser.add_argument(
    #     "-n", "--number-batteries", type=int, default=2, dest="number_batteries"
    # )

    args = parser.parse_args()
    total = count_accessible_rolls(args.rolls_map_path)

    print(total)
