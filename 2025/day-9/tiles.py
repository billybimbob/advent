#! /usr/bin/env python3

from argparse import ArgumentParser
from typing import NamedTuple, Iterable, Optional
from collections import defaultdict
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


def find_largest_area(tile_positions: list[Position], only_outline: bool) -> int:
    if len(tile_positions) <= 1:
        return 0

    if only_outline:
        outline = trace_outline(tile_positions)
        x_bounds = get_x_bounds(outline)
    else:
        x_bounds = None

    if only_outline and not x_bounds:
        return 0

    max_area = 0
    print('getting max area')

    tile_cache = dict[Position, bool]()
    count = 0

    def is_tile(x: int, y: int) -> bool:
        if not outline:
            return False

        pos = Position(x, y)
        cached_check = tile_cache.get(pos, None)

        if cached_check is not None:
            return cached_check

        if pos in outline:
            tile_cache[pos] = True
            return True

        x_ranges = x_bounds.get(y, None)
        if not x_ranges:
            tile_cache[pos] = False
            return False

        hits = 0
        for cx in x_ranges:
            if cx > x:
                hits += 1

        hit_check = is_inside(hits)
        tile_cache[pos] = hit_check
        return hit_check

    for pair in get_tile_pairs(tile_positions):
        area = get_area(pair)
        if area <= max_area:
            continue

        count += 1

        if x_bounds is None:
            max_area = area
            continue

        is_in_bounds = True
        a, b = pair

        start_x, end_x = (a.x, b.x) if a.x <= b.x else (b.x, a.x)
        start_y, end_y = (a.y, b.y) if a.y <= b.y else (b.y, a.y)

        if count % 1_000 == 0:
            print('checking bounds', count)

        for y in range(start_y, end_y + 1):
            if not is_tile(start_x, y):
                is_in_bounds = False
                break

            if not is_tile(end_x, y):
                is_in_bounds = False
                break

        if is_in_bounds:
            max_area = area

    print('finished area')

    return max_area


def get_area(pair: PositionPair) -> int:
    a, b = pair
    x_dist = abs(a.x - b.x) + 1
    y_dist = abs(a.y - b.y) + 1
    return x_dist * y_dist


def is_inside(num_collisions: int) -> bool:
    return num_collisions & 1 == 1


def get_tile_pairs(tile_positions: list[Position]) -> Iterable[PositionPair]:
    tile_positions = sorted(tile_positions)
    for i in range(len(tile_positions)):
        a = tile_positions[i]
        for j in range(i, len(tile_positions)):
            b = tile_positions[j]
            yield PositionPair(a, b)


def trace_outline(tile_positions: list[Position]) -> Optional[set[Position]]:
    positions_by_x = defaultdict[int, list[int]](list)
    positions_by_y = defaultdict[int, list[int]](list)

    for x, y in tile_positions:
        positions_by_x[x].append(y)
        positions_by_y[y].append(x)

    outline_positions = set[Position]()

    for x, y in tile_positions:
        possible_up = []
        possible_down = []
        added_y = False

        for py in positions_by_x[x]:
            if py > y:
                possible_up.append(py)
            elif py < y:
                possible_down.append(py)

        if is_inside(len(possible_up)):
            end_y = min(possible_up)
            outline_positions.update(Position(x, ty) for ty in range(y, end_y + 1))
            added_y = True

        if is_inside(len(possible_down)):
            start_y = max(possible_down)
            outline_positions.update(Position(x, ty) for ty in range(start_y, y + 1))
            added_y = True

        if not added_y:
            return None

        possible_left = []
        possible_right = []
        added_x = False

        for px in positions_by_y[y]:
            if px < x:
                possible_left.append(px)
            elif px > x:
                possible_right.append(px)

        if is_inside(len(possible_left)):
            start_x = max(possible_left)
            outline_positions.update(Position(tx, y) for tx in range(start_x, x + 1))
            added_x = True

        if is_inside(len(possible_right)):
            end_x = min(possible_right)
            outline_positions.update(Position(tx, y) for tx in range(x, end_x + 1))
            added_x = True

        if not added_x:
            return None

    return outline_positions


def get_x_bounds(outline: Optional[set[Position]]) -> dict[int, list[int]]:
    x_bounds = dict[int, list[int]]()
    if not outline:
        return x_bounds

    outline_by_y = defaultdict[int, list[int]](list)
    for x, y in outline:
        outline_by_y[y].append(x)

    for y, xs in outline_by_y.items():
        if len(xs) < 2:
            continue

        xs = sorted(xs)
        dedupe_xs = [xs[0]]

        for i in range(1, len(xs) - 1):
            curr_x = xs[i]
            last_x = xs[i-1]
            next_x = xs[i+1]

            if curr_x > last_x + 1:
                dedupe_xs.append(curr_x)
                continue

            if curr_x < next_x - 1:
                dedupe_xs.append(curr_x)
                continue

        dedupe_xs.append(xs[-1])
        x_bounds[y] = dedupe_xs

    return x_bounds


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('tile_map')
    parser.add_argument('-o', '--outline', action='store_true')
    args = parser.parse_args()

    positions = read_tile_positions(args.tile_map)
    max_area = find_largest_area(positions, args.outline)
    print(max_area)
