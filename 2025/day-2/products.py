#! /usr/bin/env python3

from argparse import ArgumentParser
import re


def scan_total_invalid_ids(id_ranges_path: str) -> int:
    total_invalid_ids = 0

    with open(id_ranges_path, "r") as f:
        for line in f:
            for id_range in line.split(","):

                match = re.match(r"(\d+)-(\d+)", id_range)
                if not match:
                    continue

                start = int(match.group(1))
                end = int(match.group(2))

                invalid_ids = sum(
                    i for i in range(start, end + 1) if is_invalid_id(str(i))
                )
                total_invalid_ids += invalid_ids

    return total_invalid_ids


def is_invalid_id(id: str) -> bool:
    id_len = len(id)

    for i in range(1, id_len):
        if id_len % i != 0:
            continue

        target = id[:i]
        all_match = all(target == id[j : j + i] for j in range(i, id_len, i))

        if all_match:
            return True

    return False


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("id_ranges_path")
    parser.add_argument("-e", "--extra-checks", action="store_false")

    args = parser.parse_args()
    total = scan_total_invalid_ids(args.id_ranges_path)

    print(total)
