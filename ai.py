import pygame
from board import *


def score(h, x, y, pos):
    score = 0
    for item in h[x][y]:
        p, s, d, w = item
        if p != pos:
            score += s
    return score


def dirs():
    return [NORTH, EAST, SOUTH, WEST]


def rel(pos, dir):
    x, y = pos
    dx, dy = dir
    return x + dx, y + dy


def rel2(pos, dir):
    x, y = pos
    dx, dy = dir
    return x + dx * 2, y + dy * 2


def manhatten(ax, ay, bx, by):
    return abs(bx - ax) + abs(by - ay)


def manhetten(start, finish):
    sx, sy = start
    fx, fy = finish
    return max(0, 4 - max(abs(sy - fy), abs(sx - fx)))


def end(pos, path):
    end = pos
    for hop in path:
        end = rel2(end, hop)
    return end


def di(dir):
    return 'N' if dir == NORTH else 'E' if dir == EAST else 'W' if dir == WEST else 'S'


def print_h(ha):
    for j in range(8):
        x = ''
        for i in range(8):
            items = ha[i][j]
            if len(items) == 0:
                x += '- '

            x += ' |'
            for item in ha[i][j]:
                p, s, d, w = item
                x += str(s) + di(d) + str(w) + ' '
            x += '| '
        print(x)


class Ai:
    def __init__(self, graphics, board):
        self.empty_middle = None
        self.last_mode = None
        self.last_line = None
        self.turn = 1
        self.graphics = graphics
        self.board = board
        self.magenta = False
        self.opponent_help_anti_bonus = -60
        self.print_wm = False

    def steps(self, pos):
        result = []
        for dir in dirs():
            dest = rel(pos, dir)
            if self.board.on_board(dest):
                result.append(dir)
        return result

    def legal_steps(self, pos):
        result = []
        for dir in self.steps(pos):
            dest = rel(pos, dir)
            if self.board.location(dest).occupant is None:
                result.append(dir)
        return result

    def hops(self, pos):
        result = []
        for dir in self.steps(pos):
            step = rel(pos, dir)
            hop = rel2(pos, dir)
            b = self.board
            if b.on_board(hop) and b.location(hop).occupant is None and b.location(step).occupant is not None:
                result.append(dir)
        return result

    def at_home(self, pos):
        x, y = pos
        return x >= 4 and (self.magenta == (y < 4))

    def at_dest(self, pos):
        x, y = pos
        return x >= 4 and (self.magenta == (y >= 4))

    def worth_moving(self, start, finish, opponent):
        if self.turn > 50:
            self.print_wm = True
        sx, sy = start
        fx, fy = finish
        val = self.magenta != opponent
        
        em = self.empty_middle
        
        sign = 1 if val else -1
        horizontal_pull = fx - sx if (fy > 4) == val else 0
        vertical_pull = (fy - sy) * sign if not self.last_mode else 0
        homestart = manhetten(start, (7, 0) if val else (7, 7))
        homefinish = manhetten(finish, (7, 0) if val else (7, 7))
        deststart = manhetten(start, (7, 7) if val else (7, 0))
        destfinish = manhetten(finish, (7, 7) if val else (7, 0))
        delta = manhatten(sx, sy, 4, em) - manhatten(fx, fy, 4, em)
        pull = vertical_pull + horizontal_pull + delta if deststart == 0 else 0
        return pull + self.turn * (homestart - homefinish) + destfinish - deststart

    def evaluate(self, pos, path, helpers, opponent_helpers):
        if len(path) == 0:
            return 0
        start = pos
        end = pos

        color = MAGENTA if self.magenta else GREEN
        opponent_pieces = 0
        for hop in path:
            bridge = rel(end, hop)
            if self.board.location(bridge).occupant.color != color:
                opponent_pieces += 1
            end = rel2(end, hop)

        bonus = 0
        sx, sy = start
        ex, ey = end

        add_score = score(helpers['add'], ex, ey, pos)

        if not self.last_mode:
            bonus += 20 * add_score

        rem_score = score(helpers['rem'], sx, sy, end)
        bonus += 20 * rem_score

        opp_add_score = score(opponent_helpers['add'], ex, ey, None)

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_add_score

        opp_rem_score = score(opponent_helpers['rem'], sx, sy, end)

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_rem_score

        e = self.worth_moving(start, end, False)
        fe = (20 + 25 * opponent_pieces) * e + bonus
        return [fe, e, opponent_pieces, self.turn, add_score, rem_score, opp_add_score, opp_rem_score]

    def evaluate_step(self, pos, dir, helpers, opponent_helpers):
        start = pos
        end = rel(pos, dir)

        bonus = 0

        sx, sy = start
        ex, ey = end

        add_score = score(helpers['add'], ex, ey, pos)

        if not self.last_mode:
            bonus += 20 * add_score
        rem_score = score(helpers['rem'], sx, sy, end)
        bonus += 20 * rem_score

        bonus += helpers['step'][sx][sy][dirs().index(dir)]

        opp_add_score = score(opponent_helpers['add'], ex, ey, None)

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_add_score
        opp_rem_score = score(opponent_helpers['rem'], sx, sy, end)

        if not self.last_mode:
            bonus += self.opponent_help_anti_bonus * opp_rem_score

        e = self.worth_moving(start, end, False)
        fe = 10 * e + bonus
        return [fe, e, self.turn, add_score, rem_score, opp_add_score, opp_rem_score]

    def hops_helpers(self, pos, path, travelled, helpers_add, helpers_step, opponent):
        result = []
        potential_blockers_to_remove = []
        for dir in self.steps(pos):
            step = rel(pos, dir)
            hop = rel2(pos, dir)
            hx, hy = hop

            if self.board.on_board(hop) and not travelled[hx][hy]:
                step_piece = self.board.location(step).occupant
                hop_piece = self.board.location(hop).occupant

                if hop_piece is None and step_piece is not None:
                    result.append(dir)

                elif hop_piece is not None and step_piece is not None:

                    w = self.worth_moving(pos, hop, opponent)

                    if w > 0:
                        s, way = path
                        first = pos
                        if len(way) > 0:
                            first = rel2(s, way[0])

                        potential_blockers_to_remove.append([first, hop, dir, w])

                    if (hop_piece.color == MAGENTA) == self.magenta:
                        di = 0
                        for dir2 in self.steps(hop):
                            step2 = rel(hop, dir2)
                            hop2 = rel2(hop, dir2)
                            if hop2 != pos and self.board.on_board(hop2):
                                step_piece2 = self.board.location(step2).occupant
                                hop_piece2 = self.board.location(hop2).occupant
                                if self.worth_moving(pos, hop2, opponent) > 0:
                                    if hop_piece2 is None and step_piece2 is None:
                                        helpers_step[hx][hy][di] += 1
                            di += 1

                elif hop_piece is None and step_piece is None:
                    sx, sy = step
                    w = self.worth_moving(pos, hop, opponent)
                    if w > 0:
                        helpers_add[sx][sy].append([pos, 1, dir, w])

        return [result, potential_blockers_to_remove]

    def traverse(self, pos, path, travelled, helpers_add, helpers_rem, helpers_step, opponent):
        hops, blockers = self.hops_helpers(pos, path, travelled, helpers_add, helpers_step, opponent)
        if len(hops) == 0:
            return [[path, blockers]]
        results = [[path, blockers]] if opponent else []
        for hop in hops:
            x, y = rel2(pos, hop)
            if not travelled[x][y]:
                travelled[x][y] = True
                start, way = path
                way = way.copy()
                way.append(hop)
                results += self.traverse((x, y), [start, way], travelled, helpers_add, helpers_rem, helpers_step, opponent)
                travelled[x][y] = False
        return results

    def helpers(self, opponent):
        helpers_add = [[[] for i in range(8)] for i in range(8)]
        helpers_rem = [[[] for i in range(8)] for i in range(8)]
        helpers_step = [[[0] * 4 for i in range(8)] * 8 for i in range(8)]

        hops = []
        for x in range(8):
            for y in range(8):
                piece = self.board.location((x, y)).occupant
                if piece is not None and (((piece.color == MAGENTA) == self.magenta) != opponent):
                    travelled = [[False] * 8 for i in range(8)]
                    travelled[x][y] = True
                    path = [(x, y), []]
                    results = self.traverse((x, y), path, travelled, helpers_add, helpers_rem, helpers_step, opponent)
                    hops.append([(x, y), results])
                    if len(results) == 1 or opponent:
                        for result in results:
                            p, b = result
                            s, w = p

                            for (pos, hop, dir, w) in b:
                                hx, hy = hop
                                helpers_rem[hx][hy].append([pos, 1, dir, w])

        return {'add': helpers_add, 'rem': helpers_rem, 'step': helpers_step, 'hops': hops}

    def show_moves(self, start, is_hop, moves):
        piece = start
        if is_hop:
            for hop in moves:
                dest = rel2(piece, hop)
                self.board.move_piece(piece, dest)
                piece = dest
                self.graphics.screen.blit(self.graphics.background, (0, 0))
                self.graphics.draw_board_pieces(self.board)
                if self.graphics.message:
                    self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
                pygame.display.update()
                pygame.time.delay(500)
        else:
            dest = rel(start, moves)
            self.board.move_piece(start, dest)
            self.graphics.screen.blit(self.graphics.background, (0, 0))
            self.graphics.draw_board_pieces(self.board)
            if self.graphics.message:
                self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
            pygame.display.update()

    def last_green_line(self):
        last_completed_line = -1
        for y in range(4):
            for x in range(4, 8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is None or piece.color != GREEN:
                    return last_completed_line
            last_completed_line = y
        return last_completed_line

    def last_magenta_line(self):
        last_completed_line = 8
        for y in reversed(range(4, 8)):
            for x in range(4, 8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is None or piece.color != MAGENTA:
                    return last_completed_line
            last_completed_line = y
        return last_completed_line

    def act(self, turn):
        self.turn = turn
        best_is_hop = False
        best_move = None
        start = None
        best_score = None

        self.last_line = self.last_magenta_line() if self.magenta else self.last_green_line()
        self.last_mode = self.last_line != -1 and self.last_line != 8
        self.empty_middle = (4 + self.last_line - 1) >> 1 if self.magenta else (3 + self.last_line + 1) >> 1

        helpers = self.helpers(False)
        opponent_helpers = self.helpers(True)
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
                    f = end(s, p)
                    w = self.worth_moving(s, f, False)
                    e, we, op, t, ads, rs, oas, ors = self.evaluate(s, p, helpers, opponent_helpers)
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
                        score, we, t, ads, rs, oas, ors = self.evaluate_step(pos, move, helpers, opponent_helpers)
                        if best_score is None or score > best_score:
                            start = pos
                            best_is_hop = False
                            best_move = move
                            best_score = score

        if best_score is not None:
            self.show_moves(start, best_is_hop, best_move)

    def turn_magenta(self, turn):
        self.magenta = True
        self.act(turn)

    def turn_green(self, turn):
        self.magenta = False
        self.act(turn)

