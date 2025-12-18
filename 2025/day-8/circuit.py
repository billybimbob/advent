#! /usr/bin/env python3

from collections.abc import Iterable
from typing import NamedTuple, Union
from argparse import ArgumentParser
import re
import math


class Position(NamedTuple):
    x: int
    y: int
    z: int


class PositionPair(NamedTuple):
    a: Position
    b: Position
    distance: float


def product(values: Iterable[int], start=1) -> int:
    result = start
    for v in values:
        result *= v
    return result


def read_junction_boxes(junctions_file: str) -> list[Position]:
    junction_boxes = list[Position]()

    with open(junctions_file, "r") as f:
        for line in f:
            match = re.match(r"^(\d+),(\d+),(\d+)$", line)
            if match:
                x = int(match[1])
                y = int(match[2])
                z = int(match[3])
                junction_boxes.append(Position(x, y, z))

    return junction_boxes


def wire_junction_boxes(
    junction_boxes: list[Position], num_connections: int
) -> list[set[Position]]:
    connections = list[set[Position]]()
    pairs = list[PositionPair]()

    for i, a in enumerate(junction_boxes):
        for b in junction_boxes[i:]:
            distance = math.dist(a, b)
            if distance != 0:
                pairs.append(PositionPair(a, b, distance))

    pairs.sort(key=lambda p: p.distance, reverse=True)

    for i in range(num_connections):
        if not pairs:
            break

        a, b, _ = pairs.pop()
        target_a: Union[set[Position], None] = None
        target_b: Union[set[Position], None] = None

        for circuit in connections:
            if a in circuit:
                target_b = circuit

            if b in circuit:
                target_a = circuit

        if target_a and target_b and target_a != target_b:
            target_a.update(target_b)
            connections.remove(target_b)

        elif target_a:
            target_a.add(a)

        elif target_b:
            target_b.add(b)

        else:
            connections.append({a, b})

    connected_boxes = {p for c in connections for p in c}
    connections.extend({b} for b in junction_boxes if b not in connected_boxes)

    return connections


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("junctions_file")
    parser.add_argument("-c", "--connections", type=int, default=1000)
    parser.add_argument("-t", "--top", type=int, default=3)

    args = parser.parse_args()

    boxes = read_junction_boxes(args.junctions_file)
    connections = wire_junction_boxes(boxes, args.connections)

    connection_lens = [len(c) for c in connections]
    answer = product(sorted(connection_lens, reverse=True)[: args.top])

    print(answer)
