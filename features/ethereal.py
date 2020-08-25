import subprocess
from functools import cached_property

import chess
from features.abstract import Features


class EtherealEval(Features):
    def __init__(self, fen, p):
        board = chess.Board(fen)
        self.turn = board.turn

        p.stdin.write("position fen {}\n".format(fen))
        p.stdin.write("go depth 1\n")

        self._eval_features = {}
        for line in iter(p.stdout.readline, ""):
            if "bestmove" in line:
                break

            if str(line).startswith("feature"):
                self._eval_features = self._parse_features(line)
                break

    def _parse_features(self, line):
        features = {f.split("=")[0]: int(f.split("=")[1]) for f in line.split()[1:]}
        if self.turn == chess.BLACK:
            new_features = {}
            for k,v in features.items():
                # reverse colors
                k = k.replace("White", "green").replace("black", "White").replace("green", "black")
                new_features[k] = v
            return new_features
        else:
            return features

    @cached_property
    def ethereal_eval_features(self):
        return self._eval_features



if __name__ == '__main__':
    ETHEREAL_PATH = "/home/pawel/projects/chesstraining/Ethereal_clone/src/Ethereal"
    p = subprocess.Popen(
        ETHEREAL_PATH,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )
    f = EtherealEval('8/5R2/r4ppk/8/4PKPP/8/8/8 b - - 0 1', p)
    features = f.features()
    print(features["ethereal_eval_features"]["ComplexityAdjustmentWhite"])
    print(features["ethereal_eval_features"]["ComplexityAdjustmentblack"])
    p.kill()