#! /usr/bin/env python3

from argparse import ArgumentParser
from typing import NamedTuple, Iterable
import re


class Position(NamedTuple):
    x: int
    y: int


class PositionPair(NamedTuple):
    a: Position
    b: Position


def read_tile_positions(tile_map_path: str) -> list[Position]:
    positions = list[Position]()

    with open(tile_map_path, 'r') as f:
        for line in f:
            match = re.match(r'^(\d+),(\d+)$', line)
            if match:
                x = int(match[1])
                y = int(match[2])
                positions.append(Position(x, y))

    return positions


def find_largest_area(tile_positions: list[Position]) -> int:
    return 0 if len(tile_positions) <= 1 else max(get_area(a, b) for a, b in get_tile_pairs(tile_positions))


def get_tile_pairs(tile_positions: list[Position]) -> Iterable[PositionPair]:
    tile_positions = sorted(tile_positions)

    for i in range(len(tile_positions)):
        a = tile_positions[i]
        for j in range(len(tile_positions) - 1, i, -1):
            b = tile_positions[j]
            yield PositionPair(a, b)


def get_area(a: Position, b: Position) -> int:
    x_dist = abs(a.x - b.x) + 1
    y_dist = abs(a.y - b.y) + 1
    return x_dist * y_dist


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('tile_map')
    args = parser.parse_args()

    positions = read_tile_positions(args.tile_map)
    max_area = find_largest_area(positions)
    print(max_area)
