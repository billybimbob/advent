#! /usr/bin/env python3

from argparse import ArgumentParser
from typing import NamedTuple
from enum import Enum
import re


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"


class RotationStep(NamedTuple):
    dial: int
    zeros: int
    extra_zeros: int = 0


class RotationResult(NamedTuple):
    steps: list[RotationStep]
    zeros: int


def find_rotation_zeros(
    start: int, max_value: int, instructions_path: str, any_click: bool
) -> RotationResult:
    dial = start
    zeros = 0
    steps = [RotationStep(dial, zeros)]

    with open(instructions_path, "r") as f:
        for line in f:
            match = re.match(r"^([LR])(\d+)$", line)

            if not match:
                continue

            distance = int(match.group(2))
            direction = Direction.LEFT if match.group(1) == "L" else Direction.RIGHT

            step = spin(dial, distance, direction, max_value)
            dial, extra_zeros, _ = step

            if dial == 0:
                zeros += 1

            if any_click:
                zeros += extra_zeros

            steps.append(RotationStep(dial, zeros, extra_zeros))

    return RotationResult(steps, zeros)


def spin(
    current: int, distance: int, direction: Direction, max_value: int
) -> RotationStep:
    extra_clicks = distance // (max_value + 1)
    delta = distance % (max_value + 1)

    if direction == Direction.LEFT:
        delta *= -1

    new_value = current + delta
    resets = False

    if new_value < 0:
        new_value = max_value + new_value + 1
        resets = True

    elif new_value > max_value:
        new_value = new_value % (max_value + 1)
        resets = True

    if resets and new_value != 0 and current != 0:
        extra_clicks += 1

    return RotationStep(new_value, extra_clicks)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("instructions_path")
    parser.add_argument("-m", "--max-value", default=99, type=int, dest="max_value")
    parser.add_argument("-s", "--start", default=50, type=int)
    parser.add_argument("-a", "--any-click", action="store_false", dest="any_click")

    args = parser.parse_args()
    steps, rotations = find_rotation_zeros(
        args.start, args.max_value, args.instructions_path, args.any_click
    )

    print(rotations, steps)
