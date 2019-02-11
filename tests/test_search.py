import os
import chess
import chess.engine
import unittest

build_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "build-release"))
goldfish_path = os.path.join(build_path, "goldfish.x")


# Puzzles given in EPD format, see https://www.chessprogramming.org/Extended_Position_Description
# Types of puzzles:
#   1. Single line mate (dm && pv)
#       Must find correct mate distance and play out each move.
#   2. Multi-variation mate (dm)
#       Must checkmate against stockfish in given number of moves, but can choose line (i.e. more than one winning line).
#   3. Single line tactic (pv)
#       Must find the _one_ strong line and play out each move.
#
# TODO: Add more test positions once these pass.

test_cases = """
1k1r4/pp1b1R2/3q2pp/4p3/2B5/4Q3/PPP2B2/2K5 b - - dm -3; pv "d6d1 c1d1 d7g4 d1e1 d8d1"; id "Bratko-Kopec.01";
1r6/5p1k/7p/2pBp3/p1P1P3/8/1PK1Rq2/1R6 b - - dm -3; pv "f2e2 c2c1 b8g8 b2b4 g8g1"; id "https://lichess.org/wkc61nls/black#103";
6KQ/8/8/8/1kn5/8/4B3/8 w - - dm 6; id "https://lichess.org/7ghS4Sop/white#148";
""".strip().split("\n")

class TestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.system(f"cd {build_path} && cmake .. -DCMAKE_BUILD_TYPE=Release && make -j5 goldfish.x")

    def setUp(self):
        self.goldfish = chess.engine.SimpleEngine.popen_uci(goldfish_path)
        self.stockfish = chess.engine.SimpleEngine.popen_uci("stockfish")

    def tearDown(self):
        self.goldfish.quit()
        self.stockfish.quit()

    def test_puzzles(self):
        for epd in test_cases:

            board = chess.Board()
            case = board.set_epd(epd)

            # Set search limits based on puzzle type. 2x meant to give ample time to find.
            if 'dm' in case:
                search_limit = chess.engine.Limit(depth=2*abs(case["dm"]))
            elif "pv" in case:
                search_limit = chess.engine.Limit(depth=2*len(case["pv"].split()))


            if "dm" in case:
                # Check that the correct mate distance is found.
                info = self.goldfish.analyse(
                    board, search_limit, info=chess.engine.Info.ALL
                )
                self.assertEqual(case["dm"], info["score"].white().moves, f"Incorrect mate distance at puzzle {case['id']}, pv: {info['pv']}")

            if "pv" in case:
                # Check that Goldfish plays the expected line.
                # pv_us is the moves we are expected to play,
                # pv_them is any response played by the opponent (not asserted).
                pv = case["pv"].split()
                pv_us, pv_them = pv[::2], pv[1::2]

                for i, move in enumerate(pv_us):
                    output = self.goldfish.play(board, search_limit)

                    self.assertEqual(chess.Move.from_uci(move), output.move, f"Incorrect move at puzzle {case['id']}")

                    # Play our move and any follow-up from the opponent.
                    board.push(output.move)
                    # print(board, end="\n\n")
                    try:
                        board.push_uci(pv_them[i])
                        # print(board, end="\n\n")
                    except IndexError:
                        break

            elif "dm" in case:
                # We have a mate, but more than one possible line. In this case Goldfish should beat Stockfish
                # in the exact number of moves given by the mate distance.

                for move_count in range(abs(case["dm"])):
                    output = self.goldfish.play(board, search_limit)
                    board.push(output.move)

                    # Let stockfish find a move to play.
                    output = self.stockfish.play(board, search_limit)
                    board.push(output.move)
                    # print(board)

                self.assertTrue(board.is_checkmate(), f"Failed to mate in puzzle {case['id']}")

            print(f"Puzzle complete: {case['id']}")


if __name__ == "__main__":
    unittest.main()
