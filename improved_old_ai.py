import pygame
from board import *
class ImprovedOldAi():
    def __init__(self, graphics, board):
        self.graphics = graphics
        self.board = board
        self.magenta = False

    def rel(self, pos, dir):
        x, y = pos
        dx, dy = dir
        return x + dx, y + dy

    def rel2(self, pos, dir):
        x, y = pos
        dx, dy = dir
        return x + dx * 2, y + dy * 2

    def turn_green(self, turn):
        self.magenta = False
        start, dest = self.find_green(turn)
        self.board.move_piece(start, dest)
        self.graphics.screen.blit(self.graphics.background, (0, 0))
        self.graphics.draw_board_pieces(self.board)
        if self.graphics.message:
            self.graphics.screen.blit(self.graphics.text_surface_obj, self.graphics.text_rect_obj)
        pygame.display.update()

    def turn_magenta(self, turn):
        self.magenta = True
        start, dest = self.find_magenta(turn)
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

    def find_green(self, turn):
        for dir in [NORTH, WEST]:
            for y in reversed(range(4, 8)):
                for x in reversed(range(4, 8)):
                    start = (x, y)
                    piece = self.board.location(start).occupant
                    if piece is not None and piece.color == GREEN:
                        step = self.rel(start, dir)
                        hop = self.rel2(start, dir)
                        if self.board.on_board(hop):
                            sp = self.board.location(step).occupant
                            hp = self.board.location(hop).occupant
                            if sp is not None and hp is None:
                                print("Improved; s: ", start, ' h ', hop)
                                return [start, hop]
                            if sp is None:
                                print("Improved; s: ", start, ' st ', step)
                                return [start, step]
        print("All pieces moved out of the base???")

        last_completed_line = self.last_green_line()

        print("Last Green Line is: ", last_completed_line)

        for y in reversed(range(8)):
            for x in range(7):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == GREEN:
                    step = self.rel(start, EAST)
                    print('s: ', start, ' step: ', step)
                    sp = self.board.location(step).occupant
                    sx, sy = step
                    if x < 6:
                        hop = self.rel2(start, EAST)
                        hp = self.board.location(hop).occupant
                        hx, hy = hop
                        if sp is not None and hp is None and (not (hy >= 4)):
                            return [start, hop]
                    if sp is None and (not (sy >= 4)):
                        return [start, step]

        for x in range(8):
            for y in reversed(range(1, 8)):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == GREEN:
                    step = self.rel(start, NORTH)
                    sp = self.board.location(step).occupant
                    if y > 1:
                        hop = self.rel2(start, NORTH)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None and (x >= 4 or y > last_completed_line + 2):
                            print("(x >= 4: ", x, ' y > LastLine + 2: ', y, ' last line: ', last_completed_line)
                            return [start, hop]
                    if sp is None and (x >= 4 or y > last_completed_line + 1):
                        print("(x >= 4: ", x, ' y > LastLine + 1: ', y, ' last line: ', last_completed_line)
                        return [start, step]
        for y in range(last_completed_line + 1):
            for x in range(4):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == GREEN:
                    step = self.rel(start, SOUTH)
                    sp = self.board.location(step).occupant
                    if y > 1:
                        hop = self.rel2(start, SOUTH)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            print("Hoping SOUTH! x: ", x, ' y: ', y, ' last line: ', last_completed_line)
                            return [start, hop]
                    if sp is None:
                        print("Stepping SOUTH! x: ", x, ' y: ', y, ' last line: ', last_completed_line)
                        return [start, step]

        for y in reversed(range(8)):
            for x in reversed(range(1, 8)):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == GREEN:
                    step = self.rel(start, WEST)
                    sp = self.board.location(step).occupant
                    if x > 1:
                        hop = self.rel2(start, WEST)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            return [start, hop]
                    if sp is None:
                        return [start, step]
        print("Error in OLD AI. Cannot find a move")

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
    def find_magenta(self, turn):
        for dir in [SOUTH, WEST]:
            for y in range(4):
                for x in reversed(range(4, 8)):
                    start = (x, y)
                    piece = self.board.location(start).occupant
                    if piece is not None and piece.color == MAGENTA:
                        step = self.rel(start, dir)
                        hop = self.rel2(start, dir)
                        if self.board.on_board(hop):
                            sp = self.board.location(step).occupant
                            hp = self.board.location(hop).occupant
                            if sp is not None and hp is None:
                                print("Improved; s: ", start, ' h ', hop)
                                return [start, hop]
                            if sp is None:
                                print("Improved; s: ", start, ' st ', step)
                                return [start, step]
        print("All pieces moved out of the base???")
        last_completed_line = self.last_magenta_line()

        for x in range(7):
            for y in range(8):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == MAGENTA:
                    step = self.rel(start, EAST)
                    sp = self.board.location(step).occupant
                    sx, sy = step
                    if x < 6:
                        hop = self.rel2(start, EAST)
                        hp = self.board.location(hop).occupant
                        hx, hy = hop
                        if sp is not None and hp is None and (not (hx >= 4 > hy)):
                            return [start, hop]
                    if sp is None and (not (sx >= 4 > sy)):
                        return [start, step]

        for x in reversed(range(8)):
            for y in range(7):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == MAGENTA:
                    step = self.rel(start, SOUTH)
                    sp = self.board.location(step).occupant
                    if y < 6:
                        hop = self.rel2(start, SOUTH)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None and (x >= 4 or y < last_completed_line - 2):
                            return [start, hop]
                    if sp is None and (x >= 4 or y < last_completed_line - 1):
                        return [start, step]

        for x in range(1, 8):
            for y in reversed(range(8)):
                start = (x, y)
                piece = self.board.location(start).occupant
                if piece is not None and piece.color == MAGENTA:
                    step = self.rel(start, WEST)
                    sp = self.board.location(step).occupant
                    if x > 1:
                        hop = self.rel2(start, WEST)
                        hp = self.board.location(hop).occupant
                        if sp is not None and hp is None:
                            return [start, hop]
                    if sp is None:
                        return [start, step]
        print("Error in OLD AI. Cannot find a move")
