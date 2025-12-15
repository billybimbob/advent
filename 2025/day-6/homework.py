#! /usr/bin/env python3

from argparse import ArgumentParser
from collections import defaultdict
from collections.abc import Iterable


def product(values: Iterable[int], start=1) -> int:
    result = start
    for v in values:
        result *= v
    return result


def parse_column(column: list[str]) -> int:
    return int("".join(column))


def total_transposed_values(agg_line: str, values: list[list[str]]) -> int:
    total = 0
    column_width = 0
    operation = ""

    for i, letter in enumerate(agg_line):
        if letter.isspace():
            column_width += 1
            continue

        if operation:
            target_columns = values[i - 1 - column_width : i - 1]

            if operation == "+":
                total += sum(parse_column(num_str) for num_str in target_columns)
            elif operation == "*":
                total += product(parse_column(num_str) for num_str in target_columns)

        column_width = 0
        operation = letter

    if operation:
        target_columns = values[len(agg_line) - 1 - column_width : len(agg_line)]

        if operation == "+":
            total += sum(parse_column(num_str) for num_str in target_columns)
        elif operation == "*":
            total += product(parse_column(num_str) for num_str in target_columns)

    return total


def solve_ceph_problem(homework_file: str) -> int:
    total_answer = 0

    with open(homework_file, "r") as f:
        transposed_values = list[list[str]]()
        for line in f:
            if not line:
                continue

            line = line.strip("\n")

            if line[0] == "*" or line[0] == "+":
                total_answer = total_transposed_values(line, transposed_values)
                continue

            if not transposed_values:
                for _ in range(len(line)):
                    transposed_values.append([])

            if len(line) != len(transposed_values):
                continue

            for i, letter in enumerate(line):
                transposed_values[i].append(letter)

    return total_answer


def solve_homework_problem(homework_file: str) -> int:
    total_answer = 0

    with open(homework_file, "r") as f:
        columns = defaultdict[int, list[int]](list)
        for line in f:
            for i, value in enumerate(line.split()):
                if value == "+":
                    total_answer += sum(v for v in columns[i])
                elif value == "*":
                    total_answer += product(v for v in columns[i])
                else:
                    columns[i].append(int(value))

    return total_answer


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("homework_file")
    parser.add_argument("-t", "--transpose", action="store_true")
    args = parser.parse_args()

    answer = (
        solve_ceph_problem(args.homework_file)
        if args.transpose
        else solve_homework_problem(args.homework_file)
    )
    print(answer)
