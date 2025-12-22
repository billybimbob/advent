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


class Range(NamedTuple):
    low: int
    high: int


def read_tile_positions(tile_map_path: str) -> list[Position]:
    positions = list[Position]()

    with open(tile_map_path, "r") as f:
        for line in f:
            match = re.match(r"^(\d+),(\d+)$", line)
            if match:
                x = int(match[1])
                y = int(match[2])
                positions.append(Position(x, y))

    return positions


def find_largest_area_all(tile_positions: list[Position]) -> int:
    return (
        max(area(pair) for pair in get_tile_pairs(tile_positions))
        if len(tile_positions) > 1
        else 0
    )


def find_largest_area_outline(tile_positions: list[Position]) -> int:
    if len(tile_positions) <= 1:
        return 0

    outline = trace_outline(tile_positions)
    if not outline:
        return 0

    x_options = sorted({x for x, _ in tile_positions})
    y_options = sorted({y for _, y in tile_positions})

    y_edges = map_edges(tile_positions, y_options)
    inside_map = list[list[bool]]()

    for y in y_options:
        row = list[bool]()
        inside_map.append(row)

        for x in x_options:
            pos = Position(x, y)

            if pos in outline:
                row.append(True)
            elif is_inside(x, y, y_edges):
                row.append(True)
            else:
                row.append(False)

    max_area = 0
    x_indices = {x: i for i, x in enumerate(x_options)}
    y_indices = {y: i for i, y in enumerate(y_options)}

    for pair in get_tile_pairs(tile_positions):
        new_area = area(pair)
        if new_area <= max_area:
            continue

        a_edge = edge_index(pair.a, x_indices, y_indices)
        b_edge = edge_index(pair.b, x_indices, y_indices)

        if not a_edge:
            continue

        if not b_edge:
            continue

        start_x, end_x = min_max(a_edge.x, b_edge.x)
        start_y, end_y = min_max(a_edge.y, b_edge.y)

        is_in_bounds = all(
            inside_map[y][x]
            for y in range(start_y, end_y + 1)
            for x in range(start_x, end_x + 1)
        )

        if is_in_bounds:
            max_area = new_area

    return max_area


def is_inside(x: int, y: int, y_edges: dict[int, list[int]]) -> bool:
    edges = y_edges.get(y, None)
    if not edges:
        return False

    hits = 0
    for ex in edges:
        if ex > x:
            hits += 1

    return hits & 1 == 1


def min_max(a: int, b: int) -> Range:
    low = min(a, b)
    high = max(a, b)
    return Range(low, high)


def area(pair: PositionPair) -> int:
    a, b = pair
    x_dist = abs(a.x - b.x) + 1
    y_dist = abs(a.y - b.y) + 1
    return x_dist * y_dist


def edge_index(
    pos: Position, x_edges: dict[int, int], y_edges: dict[int, int]
) -> Optional[Position]:
    x_edge = x_edges.get(pos.x, None)
    y_edge = y_edges.get(pos.y, None)

    if x_edge is None:
        return None

    if y_edge is None:
        return None

    return Position(x_edge, y_edge)


def get_tile_pairs(tile_positions: list[Position]) -> Iterable[PositionPair]:
    for i in range(len(tile_positions)):
        a = tile_positions[i]
        for j in range(i + 1, len(tile_positions)):
            b = tile_positions[j]
            yield PositionPair(a, b)


def trace_outline(tile_positions: list[Position]) -> set[Position]:
    # assume that the positions are ordered by adjacent
    outline_positions = set[Position]()

    if not tile_positions:
        return outline_positions

    if len(tile_positions) < 2:
        outline_positions.update(tile_positions)
        return outline_positions

    p1 = tile_positions[-1]
    outline_positions.add(p1)

    for p2 in tile_positions:
        x1, y1 = p1
        x2, y2 = p2
        outline_positions.add(p2)

        if x1 == x2:
            start_y, end_y = min_max(y1, y2)
            outline_positions.update(
                Position(x1, ty) for ty in range(start_y, end_y + 1)
            )
        elif y1 == y2:
            start_x, end_x = min_max(x1, x2)
            outline_positions.update(
                Position(tx, y1) for tx in range(start_x, end_x + 1)
            )

        p1 = p2

    return outline_positions


def map_edges(tiles: list[Position], ys: list[int]) -> dict[int, list[int]]:
    y_edges = defaultdict[int, list[int]](list)
    p1 = tiles[-1]

    for p2 in tiles:
        x1, y1 = p1
        x2, y2 = p2

        if x1 == x2:
            start_y, end_y = min_max(y1, y2)
            for ey in ys:
                if start_y < ey <= end_y:
                    y_edges[ey].append(x1)

        p1 = p2

    return y_edges


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("tile_map")
    parser.add_argument("-o", "--outline", action="store_true")
    args = parser.parse_args()

    positions = read_tile_positions(args.tile_map)
    max_area = (
        find_largest_area_outline(positions)
        if args.outline
        else find_largest_area_all(positions)
    )
    print(max_area)
