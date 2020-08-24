import json

import chess
import chess.engine


def load_puzzles(json_path):
    with open(json_path) as fp:
        data = json.load(fp)
    return data


class PuzzleProcessor:
    def __init__(self, engine_depth):
        self.engine_depth = engine_depth

    def _process_puzzle(self, puzzle, engine):
        board = chess.Board(puzzle["fen"])
        res = engine.analyse(board, chess.engine.Limit(depth=self.engine_depth))
        return {
            "depth": res["depth"],
            "score": res["score"].relative.score(),
            "mate_score": res["score"].relative.mate(),
            "pv": [move.uci() for move in res["pv"]],
        }

    def process_puzzles(self, puzzles):
        engine = chess.engine.SimpleEngine.popen_uci("/usr/local/bin/stockfish")
        for puzzle in puzzles:
            yield self._process_puzzle(puzzle, engine)
        engine.quit()


if __name__ == "__main__":
    import argparse

    from tqdm import tqdm

    parser = argparse.ArgumentParser(
        description="Augments puzzles with engine analysis."
    )
    parser.add_argument("puzzle_path", help="Path to json file with puzzles")
    parser.add_argument(
        "-d", "--engine_depth", type=int, default=10, help="Depth of the analysis"
    )
    parser.add_argument(
        "-e",
        "--extend_pv",
        action="store_true",
        help="Extends the existing pv rather than overriding it",
    )
    parser.add_argument("-o", "--output_path", help="Path for the output")

    args = parser.parse_args()

    puzzles = load_puzzles(args.puzzle_path)
    p = PuzzleProcessor(engine_depth=args.engine_depth)

    with tqdm(total=len(puzzles)) as progress_bar:
        for analysis, puzzle in zip(p.process_puzzles(puzzles), puzzles):
            puzzle["analysis"] = analysis
            progress_bar.update(1)

    if args.output_path is not None:
        with open(args.output_path, "w") as fp:
            json.dump(puzzles, fp)
    else:
        print(json.dumps(puzzles))
