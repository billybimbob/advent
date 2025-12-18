#! /usr/bin/env python3

from argparse import ArgumentParser
from collections import defaultdict


def count_beam_splits(manifold_path: str) -> int:
    total_splits = 0

    with open(manifold_path, "r") as f:
        beams = set[int]()

        for line in f:
            start_index = line.find("S")
            if start_index >= 0:
                beams.add(start_index)
                continue

            splitters = [c for c in line if c == "^"]
            new_splits = beams.intersection(splitters)

            beams.difference_update(new_splits)
            total_splits += len(new_splits)

            if len(line) <= 1:
                continue

            for split in new_splits:
                if split == 0:
                    beams.add(split + 1)
                elif split == len(line) - 1:
                    beams.add(split - 1)
                else:
                    beams.add(split + 1)
                    beams.add(split - 1)

    return total_splits


def count_beam_timelines(manifold_path: str) -> int:
    beam_counts = defaultdict[int, int](int)

    with open(manifold_path, "r") as f:
        for line in f:
            start_index = line.find("S")
            if start_index >= 0:
                beam_counts[start_index] = 1
                continue

            if len(line) <= 1:
                continue

            new_beams = defaultdict[int, int](int)

            for beam, count in beam_counts.items():
                if line[beam] == ".":
                    new_beams[beam] += count

                if line[beam] == "^":
                    if 0 <= beam < len(line) - 1:
                        new_beams[beam + 1] += count

                    if 0 < beam <= len(line) - 1:
                        new_beams[beam - 1] += count

            beam_counts = new_beams

    return sum(beam_counts.values())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("manifold_file")
    parser.add_argument(
        "-t", "--timelines", action="store_true", dest="count_timelines"
    )

    args = parser.parse_args()
    answer = (
        count_beam_splits(args.manifold_file)
        if not args.count_timelines
        else count_beam_timelines(args.manifold_file)
    )

    print(answer)
