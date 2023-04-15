import pygame
from board import *

GOLD = (255, 215, 0)
HIGH = (160, 190, 255)


class Graphics:
    def __init__(self):
        self.text_rect_obj = None
        self.text_surface_obj = None
        self.font_obj = None
        self.caption = "Corners/Куточки(Хто скорше перейде)"

        self.fps = 60
        self.clock = pygame.time.Clock()

        self.window_size = 600
        self.screen = pygame.display.set_mode((self.window_size, self.window_size + 100))
        self.background = pygame.image.load('resources/ua-board.png')

        self.square_size = self.window_size >> 3
        self.piece_size = self.square_size >> 1

        self.message = False
        self.blink = BLACK

    def setup_window(self):
        """
        This initializes the window and sets the caption at the top.
        """
        pygame.init()
        pygame.display.set_caption(self.caption)

    def update_display(self, board, legal_moves, selected_piece):
        """
        This updates the current display.
        """
        self.screen.fill("black")
        self.screen.blit(self.background, (0, 0))

        self.highlight_squares(legal_moves)
        self.draw_board_pieces(board)
        self.highlight_selected(selected_piece)

        if self.message:
            self.screen.blit(self.text_surface_obj, self.text_rect_obj)
        self.screen.blit(self.text_surface_obj2, self.text_rect_obj2)

        pygame.display.update()
        self.clock.tick(self.fps)

    def draw_board_pieces(self, board):
        """
        Takes a board object and draws all of its pieces to the display
        """
        for x in range(8):
            for y in range(8):
                if board.matrix[x][y].occupant is not None:
                    light = board.matrix[x][y].occupant.color
                    dark = MAGENTA_DARK if light == MAGENTA else GREEN_DARK
                    center = self.pixel_coords((x, y))
                    pygame.draw.circle(self.screen, dark, center, self.piece_size)
                    pygame.draw.circle(self.screen, BLACK, center, self.piece_size, 1)
                    pygame.draw.circle(self.screen, light, center, self.piece_size // 6)
                    for i in range(5):
                        pygame.draw.circle(
                            self.screen, light, center, self.piece_size * (i + 1) // 6, self.piece_size // 12
                        )

    def pixel_coords(self, board_coords):
        """
        Takes in a tuple of board coordinates (x,y)
        and returns the pixel coordinates of the center of the square at that location.
        """
        return (
            board_coords[0] * self.square_size + self.piece_size, board_coords[1] * self.square_size + self.piece_size)

    def board_coords(self, pixel):
        """
        Does the reverse of pixel_coords(). Takes in a tuple of of pixel coordinates and returns what square they are in.
        """
        return pixel[0] // self.square_size, pixel[1] // self.square_size

    def highlight_squares(self, squares):
        """
        Squares is a list of board coordinates.
        highlight_squares highlights them.
        """
        for square in squares:
            pygame.draw.rect(self.screen, HIGH, (
                square[0] * self.square_size, square[1] * self.square_size, self.square_size, self.square_size))

    def tick(self):
        self.blink = HIGH if self.blink == BLACK else BLACK

    def highlight_selected(self, origin):
        if origin is not None:
            pygame.draw.circle(
                self.screen, self.blink, self.pixel_coords(origin), self.piece_size, self.piece_size // 6
            )
            pygame.draw.circle(self.screen, BLACK, self.pixel_coords(origin), self.piece_size, 1)

    def draw_message(self, message, _):
        """
        Draws message to the screen.
        """
        self.message = True
        pygame.draw.rect(self.screen, BLACK, (0, self.window_size, self.window_size, self.window_size + 100))

        self.font_obj = pygame.font.Font('freesansbold.ttf', 30)
        self.text_surface_obj = self.font_obj.render(message, True, HIGH, BLACK)
        self.text_rect_obj = self.text_surface_obj.get_rect()
        self.text_rect_obj.center = (self.window_size >> 1, self.window_size + 20)

        self.text_surface_obj2 = self.font_obj.render(_("Press ESC to show game options"), True, HIGH, BLACK)
        self.text_rect_obj2 = self.text_surface_obj2.get_rect()
        self.text_rect_obj2.center = (self.window_size >> 1, self.window_size + 70)


