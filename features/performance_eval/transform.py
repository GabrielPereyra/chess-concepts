import re
import csv
import random

import chess


def san_variation_to_san_moves(variation: str) -> list:
    without_sidelines = re.sub(r" \([^)]+\)", "", variation)
    decorators = ["!", "?", "0-1", "1-0", "-+"]
    for dec in decorators:
        without_sidelines = without_sidelines.replace(dec, "")
    without_sidelines = without_sidelines.strip("-")
    return re.sub(r"\d+\.", "", without_sidelines.strip().replace("...", ".")).split()


class Lucas:
    @staticmethod
    def as_dict(fns_path, tag):
        puzzles = []
        with open(fns_path) as fp:
            for line in fp.readlines():
                fen, desc, variation_str = line.strip().split("|")
                san_moves = san_variation_to_san_moves(variation_str)
                pv = []
                try:
                    board = chess.Board(fen)
                    for san_move in san_moves:
                        board.push_san(san_move)
                        pv.append(board.peek().uci())
                except ValueError:
                    continue
                puzzle = {
                    "fen": fen,
                    "analysis": {"pv": pv,},
                    "tags": [tag],
                }
                puzzles.append(puzzle)
        return puzzles


class ChessPuzzleNet:

    TAGNAMES = [
        "Checkmate",
        "Stalemate",
        "MaterialGain",
        "Repetition",
        "InsufficientMaterial",
        "DiscoveredCheck",
        "DoubleCheck",
        "Fork",
        "Pin",
        "Skewer",
        "DiscoveredAttack",
        "Pin",
        "DoubleAttack",
        "Blocking",
        "CaptureAttacker",
        "CheckMateIn1",
        "CheckMateIn2",
        "CheckMateIn3",
        "CheckMateIn4",
        "CheckMateIn5",
        "CaptureAttacker",
        "IntermediateCheck",
        "TrappedPiece",
        "Unpinning",
        "Clearance",
        "Decoy",
        "Desperado",
        "AttackingPinnedPiece",
    ]

    @staticmethod
    def as_dict(csv_path, select_tag=None):
        puzzles = []
        # encoding specified to remove BOM
        # https://stackoverflow.com/a/49150749/948918
        with open(csv_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            for row in reader:
                fen = "".join(
                    row["FEN"].rsplit("/", 1)
                )  # remove additional "/" in the position part of FEN
                tags = {
                    tag_name
                    for tag_name in ChessPuzzleNet.TAGNAMES
                    if row[tag_name] == "1"
                }
                tags.add(row["MainTag"])
                if select_tag is not None and select_tag not in tags:
                    continue
                puzzle = {
                    "id": row["ID"],
                    "fen": fen,
                    "rating": row["Rating"],
                    "task": row["Task"],
                    "move1": row["Move1"],
                    "tags": sorted(tags),
                    "analysis": {"pv": [row["Move1"]]},
                }
                puzzles.append(puzzle)
        return puzzles


def as_dict(file_path, source, tag=None, select_tag=None):
    if source == "lucas":
        return Lucas.as_dict(file_path, tag)
    if source == "chesspuzzlenet":
        return ChessPuzzleNet.as_dict(file_path, select_tag=select_tag)
    raise ValueError("Unknown source '%s'" % source)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Transforms puzzle from custom format to JSON."
    )
    parser.add_argument(
        "file_path", help="Path to file with puzzle data in custom format"
    )
    parser.add_argument("source", help="Source of the puzzle, e.g. Lucas")
    parser.add_argument(
        "-a",
        "--assign_tag",
        help="Tag to assign to puzzles or None to extract tag from data",
    )
    parser.add_argument(
        "-t", "--select_tag", help="Select only puzzles with the given tag"
    )
    parser.add_argument(
        "-r",
        "--random_shuffle",
        action="store_true",
        help="Select only puzzles with the given tag",
    )
    parser.add_argument("-o", "--output_path", help="Path for the output")

    args = parser.parse_args()

    data = as_dict(
        args.file_path, args.source, tag=args.assign_tag, select_tag=args.select_tag
    )

    if args.random_shuffle:
        random.seed(47)
        random.shuffle(data)

    if args.output_path is not None:
        with open(args.output_path, "w") as fp:
            json.dump(data, fp)
    else:
        print(json.dumps(data))
