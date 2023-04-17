from ai import *

magenta_checkpoints = [(2, 1), (2, 3), (2, 5), (3, 6), (5, 6)]
green_checkpoints = [(5, 6), (5, 4), (5, 2), (4, 1), (2, 1)]


def ladder(start, path):
    fin = start
    lad = []
    for hop in path:
        bridge = rel(fin, hop)
        lad.append(bridge)
        fin = rel2(fin, hop)
    return lad


class CheckPoints(Ai):

    def pieces_kept(self, checkpoint):
        cx, cy = checkpoint
        if self.magenta:
            for i in range(cx):
                for j in range(cy):
                    piece = self.board.location((i, j)).occupant
                    if piece is not None and piece.color == MAGENTA:
                        return True
        else:
            for i in reversed(range(8, cx)):
                for j in reversed(range(8, cy)):
                    piece = self.board.location((i, j)).occupant
                    if piece is not None and piece.color == MAGENTA:
                        return True
        return False

    def checkpoints(self):
        return magenta_checkpoints if self.magenta else green_checkpoints

    def worth_moving(self, start, finish, opponent):
        if self.turn > 40:
            self.print_wm = True
        sx, sy = start
        fx, fy = finish
        val = self.magenta != opponent

        em = self.empty_middle

        sign = 1 if val else -1

        homestart = manhetten(start, (0, 0) if val else (7, 7))
        homefinish = manhetten(finish, (0, 0) if val else (7, 7))
        deststart = manhetten(start, (7, 7) if val else (0, 0))
        destfinish = manhetten(finish, (7, 7) if val else (0, 0))
        horizontal_pos = 5 if self.magenta else 2

        how_far = manhatten(sx, sy, horizontal_pos, em)

        delta = how_far - manhatten(fx, fy, horizontal_pos, em)
        # The pull is calculated only for pieces which haven't been put into destination base
        # If the piece is already reached destination base, it is no longer pulled further
        # Since Delta target is defined not as the corner point (0, 0) or (7, 7) but as a cell in a middle of
        # non-completed rows in the destination base and 3 or 5 base entrance point
        pull = delta if deststart == 0 else 0
        print(
            'Worth: ', start, finish, ' d: ', delta, ' p: ', pull,
            ' how_far ', how_far, ' hf*p ', how_far * pull, ' hs - hm: ', homestart - homefinish,
             ' df-ds: ', destfinish - deststart
        )

        # Dest Finish and Dest Start difference help to move pieces deeper into the destination base once they get there
        # Home Start and Home Finish difference help to remove pieces from the starting base
        # This difference is multiplied by the turn number because in later turns it is crucial to leave the base
        # to avoid hitting limit of leaving the base and lose

        original = how_far * pull + (homestart - homefinish) + destfinish - deststart
        checkpoints = self.checkpoints()
        fx, fy = finish
        for i in range(len(checkpoints)):
            is_start_checkpoint = False
            for j in range(i):
                if start == checkpoints[j]:
                    is_start_checkpoint = True
                    break
            if finish == checkpoints[i] and not is_start_checkpoint and self.pieces_kept(checkpoints[i]):
                original += 100
        return original

    def evaluate(self, pos, path, helpers, opponent_helpers, step_rem_helpers):
        print('checkpoing eval, ', pos, path)
        f, e, op, t, a_s, r_s, oas, ors, srs, pl = super().evaluate(
            pos, path, helpers, opponent_helpers, step_rem_helpers
        )
        if len(path) == 0:
            return [f, e, op, t, a_s, r_s, oas, ors, srs, pl]

        bonus = 0
        if not self.last_mode:
            bonus += 20 * a_s

        bonus += 20 * r_s

        bonus += (20 if self.last_mode else 10) * srs

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * oas

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * ors

        bonus += pl

        print('W: e: ', e, ' bonus: ', bonus, ' 20e: ', 20 * e)

        fe = 20 * e + bonus
        return [fe, e, op, t, a_s, r_s, oas, ors, srs, pl]

    def evaluate_step(self, pos, dir, helpers, opponent_helpers, step_rem_helpers, deferred_gratification):
        f, e, t, a_s, r_s, ss, oas, ors, srs, pl = super().evaluate_step(
            pos, dir, helpers, opponent_helpers, step_rem_helpers
        )

        start = pos
        fin = rel(pos, dir)

        bonus = 0

        sx, sy = start
        ex, ey = fin

        if not self.last_mode:
            bonus += 20 * a_s
        bonus += 20 * r_s

        bonus += (20 if self.last_mode else 10) * srs

        bonus += ss

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * oas

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * ors

        deferred, lad = deferred_gratification[ex][ey]
        if not self.last_mode and start not in lad:
            bonus += deferred

        bonus += pl

        """already_on_checkpoint = False
        for c in self.checkpoints():
            if c == start:
                already_on_checkpoint = True
        if not already_on_checkpoint:
            for c in self.checkpoints():
                cx, cy = c
                piece = self.board.location(c).occupant
                if manhatten(cx, cy, ex, ey) == 1 and piece is not None:
                    bonus += 1000"""

        fe = 10 * e + bonus
        return [fe, e, t, a_s, r_s, ss, oas, ors, srs, deferred, pl]

    def hops_only(self, pos, travelled):
        result = []
        for dir in self.steps(pos):
            step = rel(pos, dir)
            hop = rel2(pos, dir)
            hx, hy = hop

            if self.board.on_board(hop) and not travelled[hx][hy]:
                step_piece = self.board.location(step).occupant
                hop_piece = self.board.location(hop).occupant

                if hop_piece is None and step_piece is not None:
                    result.append(dir)
        return result

    def traverse_only(self, pos, path, travelled, opponent):
        start, way = path
        hops = self.hops_only(pos, travelled)
        if len(hops) == 0:
            return [way]
        results = [way] if opponent else []
        for hop in hops:
            x, y = rel2(pos, hop)
            if not travelled[x][y]:
                travelled[x][y] = True
                start, way = path
                way = way.copy()
                way.append(hop)
                results += self.traverse_only((x, y), [start, way], travelled, opponent)
                travelled[x][y] = False
        return results

    def delayed_hops(self, steps, opponent):
        hops = []
        for s in steps:
            x, y = s
            travelled = [[False] * 8 for i in range(8)]
            travelled[x][y] = True
            path = [(x, y), []]
            results = self.traverse_only((x, y), path, travelled, opponent)
            hops.append([(x, y), results])
        return hops

    def act(self, turn):
        self.turn = turn
        if self.turn == 9:
            print('9 move!')
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

        steps_destinations = []
        for x in range(8):
            for y in range(8):
                pos = (x, y)
                piece = self.board.location(pos).occupant
                if piece is not None and ((piece.color == MAGENTA) == self.magenta):
                    moves = self.legal_steps(pos)
                    for move in moves:
                        f = rel(pos, move)
                        steps_destinations.append(f)

        delayed_hops = self.delayed_hops(steps_destinations, False)
        deferred_gratification = [[[] for i in range(8)] for i in range(8)]
        for dh in delayed_hops:
            print('dh: ', dh)
            s, ways = dh
            x, y = s
            ms = None
            lad = []
            for p in ways:
                e, we, op, t, ads, rs, oas, ors, srs, pl = self.evaluate(
                    s, p, helpers, opponent_helpers, step_rem_helpers
                )
                print(
                    'Hop: s: ', s, ' p: ', p, ' f:', f, ' score: ', e, ' worth: ', we, ' ', op, ' ', t, ' ',
                    ads, ' ', rs, ' ', oas, ' ', ors, ' srs: ', srs
                )
                if ms is None or e > ms:
                    ms = e
                    lad = ladder(s, p)
            deferred_gratification[x][y] = [ms, lad]

        hops = helpers['hops']
        for hop in hops:
            s, results = hop
            for result in results:
                p, b = result
                ss, p = p
                if len(p) > 0:
                    for i in range(0, len(p)):
                        partial = p[:i + 1]
                        f = end(s, partial)
                        w = self.worth_moving(s, f, False)
                        e, we, op, t, ads, rs, oas, ors, srs, pl = self.evaluate(
                            s, p, helpers, opponent_helpers, step_rem_helpers
                        )
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
                        print('Move:', move)
                        f = rel(pos, move)
                        sc, we, t, ads, rs, ss, oas, ors, srs, df, pl = self.evaluate_step(
                            pos, move, helpers, opponent_helpers, step_rem_helpers, deferred_gratification
                        )
                        print(
                            'Steps: s:', pos, ' move: ', move, ' f: ', f, ' score: ', sc, ' worth: ', we, ' ', t, ' ',
                            ads, ' ', rs, ' ss: ', ss, ' oas: ', oas, ' ', ors, ' srs: ', srs, ' df ', df, ' pl ', pl
                        )
                        if best_score is None or sc > best_score:
                            start = pos
                            best_is_hop = False
                            best_move = move
                            best_score = sc
        print('BestScore: s:', start, ' move: ', best_move, ' score: ', best_score)

        if best_score is not None:
            self.last_turn = (start, end(start, best_move) if best_is_hop else rel(start, best_move))
            self.show_moves(start, best_is_hop, best_move)