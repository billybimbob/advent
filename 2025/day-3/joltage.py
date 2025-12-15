#! /usr/bin/env python3

from argparse import ArgumentParser


def find_total_joltage(batteries_path: str, number_batteries: int) -> int:
    with open(batteries_path, "r") as f:
        return sum(find_joltage(line.strip(), number_batteries) for line in f)


def find_joltage(bank: str, number_batteries: int) -> int:
    if not bank:
        return 0

    if len(bank) < number_batteries:
        return 0

    if len(bank) == number_batteries:
        return int(bank)

    jolts = 0
    start_index = 0

    for i in range(number_batteries):
        end_index = len(bank) - number_batteries + i + 1

        if start_index > end_index:
            remaining = int(bank[start_index - 1 :])
            return jolts + remaining

        max_rating = 0

        for j in range(start_index, end_index):
            rating = int(bank[j])
            if rating <= max_rating:
                continue

            max_rating = rating
            start_index = j + 1

        digit_shift = 10 ** (number_batteries - i - 1)
        jolts += max_rating * digit_shift

    return jolts


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("batteries_path")
    parser.add_argument(
        "-n", "--number-batteries", type=int, default=2, dest="number_batteries"
    )

    args = parser.parse_args()
    total = find_total_joltage(args.batteries_path, args.number_batteries)

    print(total)
