import json

import chess

from board.motives.fork import is_fork_simplest, is_fork_simple, is_fork_see
from board.motives.discovered_attack import (
    is_discovered_attack_simple,
    is_discovered_attack_see,
)
from board.motives.skewer import is_skewer_see
from board.motives.pin import is_pin_see
from board.mates import is_smothered_mate, is_back_rank_mate
from board.mates.arabian import (
    is_arabian_mate,
    is_arabian_mate_extended,
    is_arabian_mate_extra_extended,
)
from board.mates.mating_net import get_move_mating_net_piece_types
from board.threats import (
    creates_mate_threat,
    creates_capture_handing_piece_threat,
    creates_positive_see_capture,
)

from features.best_move import Tactic

TACTICS = [
    Tactic.FORK,
    Tactic.DISCOVERED_ATTACK,
    Tactic.PIN,
    Tactic.SKEWER,
    Tactic.SACRIFICE,
]


def tag_to_tactic(tag):
    return {
        "Skewer": Tactic.SKEWER,
        "Pin": Tactic.PIN,
        "Fork": Tactic.FORK,
        "DiscoveredAttack": Tactic.DISCOVERED_ATTACK,
        "DiscoveredCheck": Tactic.DISCOVERED_ATTACK,
        "BackrankMate": "BackrankMate",
        "SmotheredMate": "SmotheredMate",
        "ArabianMate": "ArabianMate",
    }.get(tag)


def load_puzzles(json_path, limit=None):
    with open(json_path) as fp:
        data = json.load(fp)
    if limit is not None:
        data = data[:limit]
    for puzzle in data:
        puzzle["tactics"] = {
            tactic
            for tactic in set(tag_to_tactic(tag) for tag in puzzle["tags"])
            if tactic is not None
        }
    return data


def predict_tactics(puzzle, detectors, pv_limit=None):
    fen = puzzle["fen"]
    pv = [chess.Move.from_uci(move_uci) for move_uci in puzzle["analysis"]["pv"]]
    board = chess.Board(fen)

    res = {
        tactic: [False for _ in tactic_detectors]
        for tactic, tactic_detectors in detectors.items()
    }
    for i in range(0, len(pv), 2):
        if pv_limit is not None and i >= pv_limit:
            break
        our_move = pv[i]
        fen = board.fen()
        for tactic, tactic_detectors in detectors.items():
            for j, f in enumerate(tactic_detectors):
                res[tactic][j] |= f(fen, our_move)
        board.push(our_move)
        if i + 1 < len(pv):
            their_move = pv[i + 1]
            board.push(their_move)
    return res


def get_lichess_analysis_url(fen):
    return "http://lichess.org/analysis/{}".format("_".join(fen.split(" ")))


# feel free to comment out detectors that you don't want to run (it speeds up execution)
def get_detectors():
    return {
        Tactic.FORK: [is_fork_simplest, is_fork_simple, is_fork_see,],
        Tactic.DISCOVERED_ATTACK: [
            is_discovered_attack_simple,
            is_discovered_attack_see,
        ],
        "BackrankMate": [is_back_rank_mate,],
        "SmotheredMate": [is_smothered_mate,],
        "ArabianMate": [
            is_arabian_mate,
            is_arabian_mate_extended,
            is_arabian_mate_extra_extended,
        ],
        Tactic.SKEWER: [is_skewer_see,],
        Tactic.PIN: [is_pin_see,],
    }


if __name__ == "__main__":

    import argparse

    from tqdm import tqdm
    from sklearn import metrics

    parser = argparse.ArgumentParser(
        description="Evaluates performance of our features on puzzles."
    )
    parser.add_argument("puzzle_path", help="Path to json file with augmented puzzles")
    parser.add_argument(
        "-l", "--limit", type=int, default=None, help="Limit of examples to process"
    )
    parser.add_argument(
        "-pv", "--pv_limit", type=int, default=None, help="PV length limit"
    )
    parser.add_argument(
        "-e",
        "--num_examples",
        type=int,
        default=None,
        help="Number of wrong examples to be printed",
    )

    args = parser.parse_args()

    puzzles = load_puzzles(args.puzzle_path, limit=args.limit)

    detectors = get_detectors()
    y_true = {
        tactic: [tactic in puzzle["tactics"] for puzzle in puzzles]
        for tactic in detectors.keys()
    }
    y_pred = {
        tactic: [[] for _ in tactic_detectors]
        for tactic, tactic_detectors in detectors.items()
    }

    for puzzle in tqdm(puzzles):

        predictions = predict_tactics(puzzle, detectors, pv_limit=args.pv_limit)
        for tactic, detector_preds in predictions.items():
            for i, pred in enumerate(detector_preds):
                y_pred[tactic][i].append(pred)

    for tactic, detector_preds in y_pred.items():
        num_examples = sum(y_true[tactic])
        print(tactic, f"(num_examples={num_examples})")
        yt = y_true[tactic]
        for i, f in enumerate(detectors[tactic]):
            print("\t", f.__name__)
            yp = y_pred[tactic][i]
            print("\t\tPrecision", metrics.precision_score(yt, yp))
            print("\t\tRecall", metrics.recall_score(yt, yp))
            print("\t\tF1 Score", metrics.f1_score(yt, yp))

            if args.num_examples is not None:
                tps = [puzzles[j] for j, (t, p) in enumerate(zip(yt, yp)) if t and p]
                fps = [
                    puzzles[j] for j, (t, p) in enumerate(zip(yt, yp)) if not t and p
                ]
                tns = [
                    puzzles[j] for j, (t, p) in enumerate(zip(yt, yp)) if t and not p
                ]

                print(f"\t\tTrue Positives ({len(tps)}):")
                for j, puzzle in enumerate(tps[: args.num_examples]):
                    print(
                        "\t\t\t",
                        j + 1,
                        get_lichess_analysis_url(puzzle["fen"]),
                        puzzle["analysis"]["pv"],
                        puzzle["tags"],
                    )
                print(f"\t\tFalse Positives ({len(fps)}):")
                for j, puzzle in enumerate(fps[: args.num_examples]):
                    print(
                        "\t\t\t",
                        j + 1,
                        get_lichess_analysis_url(puzzle["fen"]),
                        puzzle["analysis"]["pv"],
                        puzzle["tags"],
                    )
                print(f"\t\tTrue negatives ({len(tns)}):")
                for j, puzzle in enumerate(tns[: args.num_examples]):
                    print(
                        "\t\t\t",
                        j + 1,
                        get_lichess_analysis_url(puzzle["fen"]),
                        puzzle["analysis"]["pv"],
                        puzzle["tags"],
                    )
