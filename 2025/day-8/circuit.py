#! /usr/bin/env python3

from collections.abc import Iterable
from typing import NamedTuple, Optional
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


class ConnectionMap(NamedTuple):
    connections: list[set[Position]]
    last_pair: Optional[tuple[Position, Position]]


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
    junction_boxes: list[Position], num_connections: Optional[int]
) -> ConnectionMap:
    pairs = list[PositionPair]()
    for i, a in enumerate(junction_boxes):
        for b in junction_boxes[i:]:
            distance = math.dist(a, b)
            if distance != 0:
                pairs.append(PositionPair(a, b, distance))

    pairs.sort(key=lambda p: p.distance)
    if num_connections:
        pairs = pairs[:num_connections]

    remaining_boxes = set(junction_boxes)
    i = 0

    connections = list[set[Position]]()
    last_pair: Optional[PositionPair] = None

    while i < len(pairs) and (remaining_boxes or len(connections) > 1):
        pair = pairs[i]
        a, b, _ = pair

        if a not in remaining_boxes and b not in remaining_boxes:
            i += 1
            continue

        target_a: Optional[set[Position]] = None
        target_b: Optional[set[Position]] = None

        for circuit in connections:
            if a in circuit:
                target_b = circuit

            if b in circuit:
                target_a = circuit

        if target_a and target_b and target_a:
            target_a.update(target_b)
            connections.remove(target_b)

        elif target_a:
            target_a.add(a)

        elif target_b:
            target_b.add(b)

        else:
            connections.append({a, b})

        remaining_boxes.discard(a)
        remaining_boxes.discard(b)

        last_pair = pair
        i += 1

    connections.extend({b} for b in remaining_boxes)

    return ConnectionMap(connections, last_pair)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("junctions_file")
    parser.add_argument("-c", "--connections", type=int)
    parser.add_argument("-t", "--top", type=int)

    args = parser.parse_args()

    boxes = read_junction_boxes(args.junctions_file)
    connections, last_pair = wire_junction_boxes(boxes, args.connections)

    if args.top:
        connection_lens = [len(c) for c in connections]
        answer = product(sorted(connection_lens, reverse=True)[: args.top])
    elif last_pair:
        a, b, _ = last_pair
        answer = a.x * b.x
    else:
        answer = 0

    print(answer)
