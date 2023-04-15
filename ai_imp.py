from ai import *


class ImpAi(Ai):
    def act(self, turn):
        self.turn = turn
        best_is_hop = False
        best_move = None
        start = None
        best_score = None

        self.last_line = self.last_magenta_line() if self.magenta else self.last_green_line()
        self.last_mode = self.last_line != -1 and self.last_line != 8
        self.empty_middle = (5 + self.last_line - 1) >> 1 if self.magenta else (2 + self.last_line + 1) >> 1

        helpers = self.helpers(False)
        opponent_helpers = self.helpers(True)
        step_rem_helpers = self.step_helpers(False)
        # print_h(helpers['add'])
        # print_h(helpers['rem'])
        # print_h(opponent_helpers['add'])
        # print_h(opponent_helpers['rem'])

        hops = helpers['hops']
        for hop in hops:
            s, results = hop
            for result in results:
                p, b = result
                ss, p = p
                if len(p) > 0:
                    for i in range(1, len(p)):
                        partial = p[:i]
                        f = end(s, partial)
                        w = self.worth_moving(s, f, False)
                        e, we, op, t, ads, rs, oas, ors, srs = self.evaluate(s, p, helpers, opponent_helpers, step_rem_helpers)
                        print('Hop: s: ', s, ' p: ', p, ' f:', f, ' score: ', e, ' worth: ', we, ' w: ', w, ' ', op, ' ', t, ' ', ads, ' ', rs, ' ', oas, ' ', ors, ' srs: ', srs)

                        if best_score is None or e > best_score:
                            start = s
                            best_is_hop = True
                            best_move = p
                            best_score = e

        for x in range(8):
            for y in range(8):
                pos = (x, y)
                piece = self.board.location(pos).occupant
                if piece is not None and ((piece.color == MAGENTA) == self.magenta):
                    moves = self.legal_steps(pos)
                    for move in moves:
                        f = rel(pos, move)
                        sc, we, t, ads, rs, oas, ors, srs = self.evaluate_step(pos, move, helpers, opponent_helpers, step_rem_helpers)
                        print('Steps: s:', pos, ' move: ', move, ' f: ', f, ' score: ', sc, ' worth: ', we, ' ', t, ' ', ads, ' ', rs, ' ', oas, ' ', ors, ' srs: ', srs)
                        if best_score is None or sc > best_score:
                            start = pos
                            best_is_hop = False
                            best_move = move
                            best_score = sc
        print('BestScore: s:', start, ' move: ', best_move, ' score: ', best_score)

        if best_score is not None:
            self.last_turn = (start, end(start, best_move) if best_is_hop else rel(start, best_move))
            self.show_moves(start, best_is_hop, best_move)