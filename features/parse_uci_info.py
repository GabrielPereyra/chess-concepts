import re
from typing import List

import chess
from chess.engine import Cp, INFO_ALL, INFO_CURRLINE, INFO_PV, INFO_REFUTATION, INFO_SCORE, Info, InfoDict, LOGGER, \
    Mate, \
    PovScore

UCI_REGEX = re.compile(r"^[a-h][1-8][a-h][1-8][pnbrqk]?|[PNBRQK]@[a-h][1-8]|0000\Z")

def _parse_uci_info_fixed(arg: str, root_board: chess.Board, selector: Info = INFO_ALL) -> InfoDict:
    info: InfoDict = {}
    if not selector:
        return info

    tokens = arg.split(" ")
    while tokens:
        parameter = tokens.pop(0)

        if parameter == "string":
            info["string"] = " ".join(tokens)
            break
        elif parameter in ["depth", "seldepth", "nodes", "multipv", "currmovenumber", "hashfull", "nps", "tbhits", "cpuload"]:
            try:
                info[parameter] = int(tokens.pop(0))  # type: ignore
            except (ValueError, IndexError):
                LOGGER.error("exception parsing %s from info: %r", parameter, arg)
        elif parameter == "time":
            try:
                info["time"] = int(tokens.pop(0)) / 1000.0
            except (ValueError, IndexError):
                LOGGER.error("exception parsing %s from info: %r", parameter, arg)
        elif parameter == "ebf":
            try:
                info["ebf"] = float(tokens.pop(0))
            except (ValueError, IndexError):
                LOGGER.error("exception parsing %s from info: %r", parameter, arg)
        elif parameter == "score" and selector & INFO_SCORE:
            try:
                kind = tokens.pop(0)
                value = tokens.pop(0)
                if tokens and tokens[0] in ["lowerbound", "upperbound"]:
                    info[tokens.pop(0)] = True  # type: ignore
                if kind == "cp":
                    info["score"] = PovScore(Cp(int(value)), root_board.turn)
                elif kind == "mate":
                    info["score"] = PovScore(Mate(int(value)), root_board.turn)
                else:
                    LOGGER.error("unknown score kind %r in info (expected cp or mate): %r", kind, arg)
            except (ValueError, IndexError):
                LOGGER.error("exception parsing score from info: %r", arg)
        elif parameter == "currmove":
            try:
                info["currmove"] = chess.Move.from_uci(tokens.pop(0))
            except (ValueError, IndexError):
                LOGGER.error("exception parsing currmove from info: %r", arg)
        elif parameter == "currline" and selector & INFO_CURRLINE:
            try:
                if "currline" not in info:
                    info["currline"] = {}

                cpunr = int(tokens.pop(0))
                currline: List[chess.Move] = []
                info["currline"][cpunr] = currline

                board = root_board.copy(stack=False)
                while tokens and UCI_REGEX.match(tokens[0]):
                    currline.append(board.push_uci(tokens.pop(0)))
            except (ValueError, IndexError):
                LOGGER.error("exception parsing currline from info: %r, position at root: %s", arg, root_board.fen())
        elif parameter == "refutation" and selector & INFO_REFUTATION:
            try:
                if "refutation" not in info:
                    info["refutation"] = {}

                board = root_board.copy(stack=False)
                refuted = board.push_uci(tokens.pop(0))

                refuted_by: List[chess.Move] = []
                info["refutation"][refuted] = refuted_by

                while tokens and UCI_REGEX.match(tokens[0]):
                    refuted_by.append(board.push_uci(tokens.pop(0)))
            except (ValueError, IndexError):
                LOGGER.error("exception parsing refutation from info: %r, position at root: %s", arg, root_board.fen())
        elif parameter == "pv" and selector & INFO_PV:
            try:
                pv: List[str] = []
                info["pv"] = pv
                while tokens and UCI_REGEX.match(tokens[0]):
                    pv.append(tokens.pop(0))
            except (ValueError, IndexError):
                LOGGER.error("exception parsing pv from info: %r, position at root: %s", arg, root_board.fen())
        elif parameter == "wdl":
            try:
                info["wdl"] = int(tokens.pop(0)), int(tokens.pop(0)), int(tokens.pop(0))
            except (ValueError, IndexError):
                LOGGER.error("exception parsing wdl from info: %r", arg)

    return info