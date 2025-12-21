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
        print('traced with', None if outline is None else len(outline))
        allowed_tiles = fill_outline(outline)
        print('fill with', len(allowed_tiles))
    else:
        allowed_tiles = None

    if allowed_tiles is not None and not allowed_tiles:
        return 0

    max_area = 0

    for pair in get_tile_pairs(tile_positions):
        area = get_area(pair)
        if area <= max_area:
            continue

        if allowed_tiles is None:
            max_area = area
            continue

        start_x, end_x = (a.x, b.x) if a.x <= b.y else (b.x, a.x)
        all_allowed_x = all(
            Position(x, a.y) in allowed_tiles and
            Position(x, b.y) in allowed_tiles
            for x in range(start_x, end_x + 1)
        )

        if not all_allowed_x:
            continue

        start_y, end_y = (a.y, b.y) if a.y <= b.y else (b.y, a.y)
        all_allowed_y = all(
            Position(a.x, y) in allowed_tiles and
            Position(b.x, y) in allowed_tiles
            for y in range(start_y, end_y + 1)
        )

        if not all_allowed_y:
            continue

        max_area = area

    return max_area


def get_area(pair: PositionPair) -> int:
    a, b = pair
    x_dist = abs(a.x - b.x) + 1
    y_dist = abs(a.y - b.y) + 1
    return x_dist * y_dist


def is_inside(num_collisions: int) -> bool:
    return num_collisions % 2 == 1


def get_tile_pairs(tile_positions: list[Position]) -> Iterable[PositionPair]:
    tile_positions = sorted(tile_positions)
    for i in range(len(tile_positions)):
        a = tile_positions[i]
        for j in range(i, len(tile_positions)):
            b = tile_positions[j]
            yield PositionPair(a, b)

def trace_outline(tile_positions: list[Position]) -> Optional[list[Position]]:
    positions_by_x = defaultdict[int, list[Position]](list)
    positions_by_y = defaultdict[int, list[Position]](list)

    for pos in tile_positions:
        positions_by_x[pos.x].append(pos)
        positions_by_y[pos.y].append(pos)

    outline_positions = set[Position]()

    for pos in tile_positions:
        possible_left = [pl for pl in positions_by_y[pos.y] if pl.x < pos.x]
        possible_right = [pr for pr in positions_by_y[pos.y] if pr.x > pos.x]

        possible_up = [pu for pu in positions_by_x[pos.x] if pu.y > pos.y]
        possible_down = [pd for pd in positions_by_x[pos.x] if pd.y < pos.y]

        added_x = False
        added_y = False

        if is_inside(len(possible_left)):
            target_left = max(possible_left, key=lambda p: p.x)
            if target_left.y != pos.y:
                return None

            outline_positions.update(Position(x, pos.y) for x in range(target_left.x, pos.x + 1))
            added_x = True

        if is_inside(len(possible_right)):
            target_right = min(possible_right, key=lambda p: p.x)
            if target_right.y != pos.y:
                return None

            outline_positions.update(Position(x, pos.y) for x in range(pos.x, target_right.x + 1))
            added_x = True

        if is_inside(len(possible_up)):
            target_up = min(possible_up, key=lambda p: p.y)
            if target_up.x != pos.x:
                return None

            outline_positions.update(Position(pos.x, y) for y in range(pos.y, target_up.y + 1))
            added_y = True

        if possible_down:
            target_down = max(possible_down, key=lambda p: p.y)
            if target_down.x != pos.x:
                return None

            outline_positions.update(Position(pos.x, y) for y in range(target_down.y, pos.y + 1))
            added_y = True

        if not added_x:
            return None

        if not added_y:
            return None

    return outline_positions


def fill_outline(outline_positions: Optional[set[Position]]) -> set[Position]:
    fill_positions = set[Position]()

    if not outline_positions:
        return fill_positions

    return fill_positions

    outline_by_y = dict[int, set[int]]()

    for out_p in outline_positions:
        fill_positions.add(out_p)

        if out_p.y in outline_by_y:
            outline_by_y[out_p.y].add(out_p.x)
        else:
            outline_by_y[out_p.y] = {out_p.x}

    for out_x, out_y in outline_positions:
        bound_xs = outline_by_y[out_y]
        if not bound_xs:
            continue

        if Position(out_x + 1, out_y) not in fill_positions:
            right_xs = [b for b in bound_xs if b > out_x]

            # ray cast position right, and if even outlines hit, it's outside
            if is_inside(len(right_xs)):
                end_x = min(right_xs)
                fill_positions.update(Position(x, out_y) for x in range(out_x + 1, end_x))

        if Position(out_x - 1, out_y) not in fill_positions:
            left_xs = [b for b in bound_xs if b < out_x]

            if is_inside(len(left_xs)):
                end_x = max(left_xs)
                fill_positions.update(Position(x, out_y) for x in range(end_x, out_x, -1))

    return fill_positions


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('tile_map')
    parser.add_argument('-o', '--outline', action='store_true')
    args = parser.parse_args()

    positions = read_tile_positions(args.tile_map)
    max_area = find_largest_area(positions, args.outline)
    print(max_area)
