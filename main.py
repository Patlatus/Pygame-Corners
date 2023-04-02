"""
Loosely based upon https://github.com/quyq/Pygame-Checkers
However, here a completely different game is built while still on chessboard.
Colors of the board cells and pieces were changed to match the original game implemented in Delphi
"""
import pygame, sys
from pygame.locals import *

from graphics import Graphics
from board import *

pygame.font.init()

class Game:
	"""
	The main game control.
	"""

	run = True

	def __init__(self):
		self.green = 1
		self.magenta = 1
		self.end = False
		self.graphics = Graphics()
		self.board = Board()
		
		self.turn = GREEN
		self.selected_piece = None # a board location. 
		self.hop = False
		self.selected_legal_moves = []

	def setup(self):
		"""Draws the window and board at the beginning of the game"""
		self.graphics.setup_window()

	def event_loop(self):
		"""
		The event loop. This is where events are triggeMAGENTA 
		(like a mouse click) and then effect the game state.
		"""
		self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos()) # what square is the mouse in?
		if self.selected_piece != None:
			self.selected_legal_moves = self.board.legal_moves(self.selected_piece, self.hop)

		for event in pygame.event.get():

			if event.type == QUIT:
				self.terminate_game()
			if not self.end and event.type == MOUSEBUTTONDOWN and self.board.on_board(self.mouse_pos):
				if self.hop == False:
					if self.board.location(self.mouse_pos).occupant != None and self.board.location(self.mouse_pos).occupant.color == self.turn:
						self.selected_piece = self.mouse_pos

					elif self.selected_piece != None and self.mouse_pos in self.board.legal_moves(self.selected_piece):

						self.board.move_piece(self.selected_piece, self.mouse_pos)
					
						if self.mouse_pos not in self.board.adjacent(self.selected_piece):
							self.hop = True
							self.selected_piece = self.mouse_pos

						else:
							self.end_turn()

				elif self.hop == True:
					if self.selected_piece != None and self.mouse_pos in self.board.legal_moves(self.selected_piece, self.hop):
						self.board.move_piece(self.selected_piece, self.mouse_pos)
						self.selected_piece = self.mouse_pos
					else:
						self.end_turn()

	def update(self):
		"""Calls on the graphics class to update the game display."""
		self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)

	def terminate_game(self):
		Game.run = False

	def main(self):
		""""This executes the game and controls its flow."""
		self.setup()

		self.graphics.draw_message("Next Turn: Green. Counter: " + str(self.green))

		while Game.run: # main game loop
			self.event_loop()
			self.update()

		pygame.quit()
		sys.exit()

	def end_turn(self):
		"""
		End the turn. Switches the current player. 
		end_turn() also checks for and game and resets a lot of class attributes.
		"""
		if self.post_check_for_endgame():
			self.end = True
			if self.turn == GREEN:
				self.graphics.draw_message("MAGENTA WINS!")
			else:
				self.graphics.draw_message("GREEN WINS!")
			self.selected_piece = None
			self.selected_legal_moves = []
			self.hop = False
			return

		if self.turn == GREEN:
			self.green += 1
			self.turn = MAGENTA
			self.graphics.draw_message("Next Turn: Magenta. Counter: " + str(self.magenta))
		else:
			self.magenta += 1
			self.turn = GREEN
			self.graphics.draw_message("Next Turn: Green. Counter: " + str(self.green))

		self.selected_piece = None
		self.selected_legal_moves = []
		self.hop = False

		if self.pre_check_for_endgame():
			self.end = True
			if self.turn == GREEN:
				self.graphics.draw_message("MAGENTA WINS!")
			else:
				self.graphics.draw_message("GREEN WINS!")
	def check_if_magenta_completes(self):
		for x in range(5, 8):
			for y in range(5, 8):
				piece = self.board.location((x, y)).occupant
				if piece is None or piece.color != MAGENTA:
					return False
		return True

	def check_if_green_completes(self):
		for x in range(3):
			for y in range(3):
				piece = self.board.location((x, y)).occupant
				if piece is None or piece.color != GREEN:
					return False
		return True

	def check_if_magenta_stays(self):
		for x in range(3):
			for y in range(3):
				piece = self.board.location((x, y)).occupant
				if piece is not None and piece.color == MAGENTA:
					return True
		return False

	def check_if_green_stays(self):
		for x in range(5, 8):
			for y in range(5, 8):
				piece = self.board.location((x, y)).occupant
				if piece is not None and piece.color == GREEN:
					return True
		return False

	def pre_check_for_endgame(self):
		"""
		Checks to see if a player has run out of moves or pieces. If so, then return True. Else return False.
		"""
		if self.turn == GREEN:
			if self.check_if_magenta_completes():
				return True
		if self.turn == MAGENTA:
			if self.check_if_green_completes():
				return True
		for x in range(8):
			for y in range(8):
				if self.board.location((x,y)).occupant is not None and self.board.location((x,y)).occupant.color == self.turn:
					if self.board.legal_moves((x,y)) != []:
						return False

		return True

	def post_check_for_endgame(self):
		"""
		Checks to see if a player has stayed in his field for longer than 50 turns or moves back after 50th turn
		"""
		if self.turn == GREEN:
			if self.green > 40 and self.check_if_green_stays():
				return True
		if self.turn == MAGENTA:
			if self.magenta > 40 and self.check_if_magenta_stays():
				return True

		return False

def main():
	game = Game()
	game.main()

if __name__ == "__main__":
	main()