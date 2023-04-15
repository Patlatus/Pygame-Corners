"""
Loosely based upon https://github.com/quyq/Pygame-Checkers
However, here a completely different game is built while still on chessboard.
Colors of the board cells and pieces were changed to match the original game implemented in Delphi
"""
import locale
import pygame, sys
from pygame.locals import *
from enum import Enum
from graphics import Graphics
from board import *
from button import Button
from ai import Ai
from improved_old_ai import ImprovedOldAi
import gettext

pygame.font.init()

_ = gettext.gettext


class Level(Enum):
	OLD_IMP = 1
	NEW = 2


class Game:
	"""
	The main game control.
	"""

	run = True

	def __init__(self):
		global _

		self.green = 1
		self.magenta = 1
		self.end = False
		self.graphics = Graphics()
		self.board = Board()
		self.ai = Ai(self.graphics, self.board)
		self.impoldai = ImprovedOldAi(self.graphics, self.board)
		self.level = Level.NEW

		self.turn = GREEN
		self.selected_piece = None # a board location. 
		self.hop = False
		self.selected_legal_moves = []

		self.TICK = pygame.USEREVENT
		self.AI_TICK = pygame.USEREVENT + 1
		pygame.time.set_timer(self.TICK, 500)
		pygame.time.set_timer(self.AI_TICK, 1200)
		self.show_menu = False
		self.show_main_menu = False
		self.show_options = False
		self.show_level = False
		self.show_lang = False
		self.ai_green = False
		self.ai_magenta = False
		self.delay_ai = False

		self.en = gettext.gettext
		ua = gettext.translation('messages', localedir='locale', languages=['ua'])
		ua.install()
		self.ua = ua.gettext

		if locale.getdefaultlocale()[0] == 'uk_UA':
			_ = self.ua

		self.play_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 2 // 7),
								  text_input=_("RESUME GAME"), font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		self.restart_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 3 // 7),
								  text_input=_("RESTART GAME"), font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		
		self.options_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 4 // 7),
									 text_input=_("OPTIONS"), font=self.get_font(75), base_color="#d7fcd4",
									 hovering_color="White")
		self.level_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 5 // 7),
									 text_input=_("AI LEVEL"), font=self.get_font(75), base_color="#d7fcd4",
									 hovering_color="White")
		self.lang_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 6 // 7),
									 text_input=_("LANGUAGE"), font=self.get_font(75), base_color="#d7fcd4",
									 hovering_color="White")
		# pygame.image.load("assets/Quit Rect.png")
		self.quit_button = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 7 // 7),
								  text_input=_("QUIT"), font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")

		self.human_choice = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 2 // 6),
								  text_input=_("HUMAN VS HUMAN"), font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		self.ai_starts = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 3 // 6),
								  text_input=_("AI VS HUMAN"), font=self.get_font(75), base_color="#d7fcd4",
								  hovering_color="White")
		
		self.ai_strikes_back = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 4 // 6),
									 text_input=_("HUMAN VS AI"), font=self.get_font(75), base_color="#d7fcd4",
									 hovering_color="White")
		self.options_back = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 5 // 6),
							  text_input=_("BACK"), font=self.get_font(75), base_color="#d7fcd4",
							  hovering_color="White")

		self.imp_old_ai_choice = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 3 // 6),
								text_input=_("Improved Old AI: Easy"), font=self.get_font(75), base_color="#d7fcd4",
								hovering_color="White")
		
		self.new_ai_choice = Button(image=None,
									  pos=(self.graphics.window_size >> 1, self.graphics.window_size * 4 // 6),
									  text_input=_("New AI (2023): Medium"), font=self.get_font(75), base_color="#d7fcd4",
									  hovering_color="White")
		self.level_back = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 5 // 6),
								   text_input=_("BACK"), font=self.get_font(75), base_color="#d7fcd4",
								   hovering_color="White")
		self.en_choice = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 2 // 6),
								   text_input=_("English"), font=self.get_font(75), base_color="#d7fcd4",
								   hovering_color="White")
		self.ua_choice = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 3 // 6),
								text_input=_("Ukrainian"), font=self.get_font(75), base_color="#d7fcd4",
								hovering_color="White")
		self.lang_back = Button(image=None, pos=(self.graphics.window_size >> 1, self.graphics.window_size * 5 // 6),
								   text_input=_("BACK"), font=self.get_font(75), base_color="#d7fcd4",
								   hovering_color="White")



	def setup(self):
		"""Draws the window and board at the beginning of the game"""
		self.graphics.setup_window()

	def get_font(self, size):
		return pygame.font.SysFont("comicsans", 40)  # pygame.font.Font("assets/font.ttf", size)

	def process_main_menu(self, mouse_pos):
		if self.play_button.checkForInput(mouse_pos):
			self.show_main_menu = False
			self.show_menu = False
			if not self.is_human_turn() and not self.end:
				self.perform_ai_turn()
		if self.restart_button.checkForInput(mouse_pos):
			self.restart()
			self.show_main_menu = False
			self.show_menu = False
		if self.options_button.checkForInput(mouse_pos):
			self.show_main_menu = False
			self.show_options = True
		if self.level_button.checkForInput(mouse_pos):
			self.show_main_menu = False
			self.show_level = True
		if self.lang_button.checkForInput(mouse_pos):
			self.show_main_menu = False
			self.show_lang = True

		if self.quit_button.checkForInput(mouse_pos):
			self.terminate_game()

	def process_options(self, mouse_pos):
		if self.human_choice.checkForInput(mouse_pos):
			self.ai_green = False
			self.ai_magenta = False
		if self.ai_starts.checkForInput(mouse_pos):
			self.ai_green = True
			self.ai_magenta = False
		if self.ai_strikes_back.checkForInput(mouse_pos):
			self.ai_green = False
			self.ai_magenta = True
		if self.options_back.checkForInput(mouse_pos):
			self.show_options = False
			self.show_main_menu = True

	def process_level(self, mouse_pos):
		if self.imp_old_ai_choice.checkForInput(mouse_pos):
			self.level = Level.OLD_IMP
		if self.new_ai_choice.checkForInput(mouse_pos):
			self.level = Level.NEW
		if self.level_back.checkForInput(mouse_pos):
			self.show_level = False
			self.show_main_menu = True

	def process_lang(self, mouse_pos):
		global _
		self.graphics.screen.fill("black")
		if self.en_choice.checkForInput(mouse_pos):
			_ = self.en
			self.update_messages()
		if self.ua_choice.checkForInput(mouse_pos):
			_ = self.ua
			self.update_messages()
		if self.lang_back.checkForInput(mouse_pos):
			self.show_lang = False
			self.show_main_menu = True
			
	def update_messages(self):
		self.play_button.translate(_("RESUME GAME"))
		self.restart_button.translate(_("RESTART GAME"))
		self.options_button.translate(_("OPTIONS"))
		self.level_button.translate(_("AI LEVEL"))
		self.lang_button.translate(_("LANGUAGE"))
		self.quit_button.translate(_("QUIT"))

		self.human_choice.translate(_("HUMAN VS HUMAN"))
		self.ai_starts.translate(_("AI VS HUMAN"))
		
		self.ai_strikes_back.translate(_("HUMAN VS AI"))
		self.options_back.translate(_("BACK"))

		self.imp_old_ai_choice.translate(_("Improved Old AI: Easy"))
		
		self.new_ai_choice.translate(_("New AI (2023): Medium"))
		self.level_back.translate(_("BACK"))
		self.en_choice.translate(_("English"))
		self.ua_choice.translate(_("Ukrainian"))
		self.lang_back.translate(_("BACK"))

		if self.turn == GREEN:
			self.graphics.draw_message(_("Next Turn: Magenta. Counter: ") + str(self.magenta), _)
		else:
			self.graphics.draw_message(_("Next Turn: Green. Counter: ") + str(self.green), _)

	def process_menu(self, mouse_pos):
		if self.show_main_menu:
			self.process_main_menu(mouse_pos)
		elif self.show_options:
			self.process_options(mouse_pos)
		elif self.show_level:
			self.process_level(mouse_pos)
		elif self.show_lang:
			self.process_lang(mouse_pos)

	def process_human_turn(self, mouse_pos):
		cell = self.graphics.board_coords(mouse_pos)  # what square is the mouse in?
		if self.board.on_board(cell):
			if not self.hop:
				piece = self.board.location(cell).occupant
				if piece is not None and piece.color == self.turn:
					self.selected_piece = cell
				elif self.selected_piece is not None and cell in self.board.legal_moves(self.selected_piece):
					self.board.move_piece(self.selected_piece, cell)

					if cell not in adjacent(self.selected_piece):
						self.hop = True
						self.selected_piece = cell
						if len(self.board.legal_moves(cell, self.hop)) == 0:
							self.end_turn()
					else:
						self.end_turn()

			elif self.hop:
				if self.selected_piece is not None and cell in self.board.legal_moves(self.selected_piece, self.hop):
					self.board.move_piece(self.selected_piece, cell)
					self.selected_piece = cell
					if len(self.board.legal_moves(cell, self.hop)) == 0:
						self.end_turn()
				else:
					self.end_turn()

	def event_loop(self):
		"""
		The event loop. This is where events are triggered
		(like a mouse click) and then effect the game state.
		"""
		if self.selected_piece is not None:
			self.selected_legal_moves = self.board.legal_moves(self.selected_piece, self.hop)

		for event in pygame.event.get():
			if event.type == QUIT:
				self.terminate_game()

			if not self.show_menu and event.type == self.TICK:
				self.graphics.tick()

			if not self.show_menu and event.type == self.AI_TICK:
				if not self.is_human_turn() and not self.end:
					self.perform_ai_turn()

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.show_menu = not self.show_menu
					self.show_main_menu = not self.show_options and not self.show_level and not self.show_lang and self.show_menu
					if not self.is_human_turn() and not self.end:
						self.perform_ai_turn()
				if event.key == pygame.K_DELETE:
					#self.ai_magenta = False
					pass


			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse_pos = pygame.mouse.get_pos()
				if self.show_menu:
					self.process_menu(mouse_pos)
				elif not self.end and self.is_human_turn():
					self.process_human_turn(mouse_pos)

			if self.show_menu:
				if self.show_main_menu:
					self.display_main_menu()
				elif self.show_options:
					self.display_options()
				elif self.show_level:
					self.display_level()
				elif self.show_lang:
					self.display_lang()

	def is_human_turn(self):
		return not self.ai_magenta and self.turn == MAGENTA or not self.ai_green and self.turn == GREEN

	def display_main_menu(self):
		self.graphics.screen.fill("black")

		menu_text = self.get_font(100).render(_("MAIN MENU"), True, "#b68f40")
		menu_rect = menu_text.get_rect(center=(self.graphics.window_size >> 1, self.graphics.window_size // 7))

		self.graphics.screen.blit(menu_text, menu_rect)

		mouse_pos = pygame.mouse.get_pos()
		for button in [
			self.play_button, self.restart_button, self.options_button, self.level_button, self.lang_button,
			self.quit_button
		]:
			button.changeColor(mouse_pos)
			button.update(self.graphics.screen)
		pygame.display.update()

	def display_options(self):
		mouse_pos = pygame.mouse.get_pos()

		self.graphics.screen.fill("black")

		options_text = self.get_font(45).render(_("GAME OPTIONS"), True, "#b68f40")
		options_rect = options_text.get_rect(center=(self.graphics.window_size >> 1, self.graphics.window_size // 6))
		self.graphics.screen.blit(options_text, options_rect)

		self.human_choice.selected = not (self.ai_green or self.ai_magenta)
		self.ai_starts.selected = self.ai_green
		self.ai_strikes_back.selected = self.ai_magenta

		for button in [self.human_choice, self.ai_starts, self.ai_strikes_back, self.options_back]:
			button.changeColor(mouse_pos)
			button.update(self.graphics.screen)

		pygame.display.update()

	def display_level(self):
		mouse_pos = pygame.mouse.get_pos()

		self.graphics.screen.fill("black")

		options_text = self.get_font(45).render(_("AI LEVEL OPTIONS"), True, "#b68f40")
		options_rect = options_text.get_rect(
			center=(self.graphics.window_size >> 1, self.graphics.window_size // 6))
		self.graphics.screen.blit(options_text, options_rect)

		self.imp_old_ai_choice.selected = self.level == Level.OLD_IMP
		self.new_ai_choice.selected = self.level == Level.NEW

		for button in [self.imp_old_ai_choice, self.new_ai_choice, self.level_back]:
			button.changeColor(mouse_pos)
			button.update(self.graphics.screen)

		pygame.display.update()

	def display_lang(self):
		mouse_pos = pygame.mouse.get_pos()

		self.graphics.screen.fill("black")

		options_text = self.get_font(45).render(_("LANGUAGE OPTIONS"), True, "#b68f40")
		options_rect = options_text.get_rect(
			center=(self.graphics.window_size >> 1, self.graphics.window_size // 6))
		self.graphics.screen.blit(options_text, options_rect)

		self.en_choice.selected = _ == self.en
		self.ua_choice.selected = _ == self.ua

		for button in [self.en_choice, self.ua_choice, self.lang_back]:
			button.changeColor(mouse_pos)
			button.update(self.graphics.screen)

		pygame.display.update()

	def restart(self):
		self.end = False
		self.green = 1
		self.magenta = 1
		self.hop = False
		self.turn = GREEN
		self.selected_legal_moves = []
		self.selected_piece = None
		self.board.matrix = new_board()
		self.graphics.draw_message(_("Next Turn: Magenta. Counter: ") + str(self.magenta), _)
		self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)

	def update(self):
		"""Calls on the graphics class to update the game display."""
		if not self.show_menu:
			self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)


	def terminate_game(self):
		Game.run = False

	def main(self):
		""""This executes the game and controls its flow."""
		self.setup()

		self.graphics.draw_message(_("Next Turn: Green. Counter: ") + str(self.green), _)

		while Game.run: # main game loop
			self.event_loop()
			self.update()

		pygame.quit()
		sys.exit()

	def end_turn(self):
		print("End of turn")
		print("==============================================================================================")
		"""
		End the turn. Switches the current player. 
		end_turn() also checks for and game and resets a lot of class attributes.
		"""
		if self.post_check_for_endgame():
			self.end = True
			if self.turn == GREEN:
				self.graphics.draw_message(_("MAGENTA WINS!"), _)
			else:
				self.graphics.draw_message(_("GREEN WINS!"), _)
			self.selected_piece = None
			self.selected_legal_moves = []
			self.hop = False
			return

		if self.turn == GREEN:
			self.green += 1
			self.turn = MAGENTA
			self.graphics.draw_message(_("Next Turn: Magenta. Counter: ") + str(self.magenta), _)

		else:
			self.magenta += 1
			self.turn = GREEN
			self.graphics.draw_message(_("Next Turn: Green. Counter: ") + str(self.green), _)

		self.selected_piece = None
		self.selected_legal_moves = []
		self.hop = False

		if self.pre_check_for_endgame():
			self.end = True
			if self.turn == GREEN:
				self.graphics.draw_message(_("MAGENTA WINS!"), _)
			else:
				self.graphics.draw_message(_("GREEN WINS!"), _)
		#print("Checking AI Turn")
		if not self.end:
			self.perform_ai_turn()

	def get_ai(self):
		#return self.ai if self.turn != MAGENTA else self.impoldai
		match self.level:
			case Level.OLD_IMP:
				return self.impoldai
			case Level.NEW:
				return self.ai

	def perform_ai_turn(self):
		print("self.turn", self.turn, ' ai m ', self.ai_magenta)
		if self.turn == MAGENTA and self.ai_magenta:
			self.get_ai().turn_magenta(self.magenta)
			if self.post_check_for_endgame():
				self.end = True
				self.graphics.draw_message(_("GREEN WINS!"), _)
				return

			self.magenta += 1
			self.turn = GREEN
			self.graphics.draw_message(_("Next Turn: Green. Counter: ") + str(self.green), _)
			if self.pre_check_for_endgame():
				self.end = True
				self.graphics.draw_message(_("MAGENTA WINS!"), _)
				return
			print("self.turn", self.turn, ' ai g ', self.ai_green)
		elif self.turn == GREEN and self.ai_green:
			self.get_ai().turn_green(self.green)

			if self.post_check_for_endgame():
				self.end = True
				self.graphics.draw_message(_("MAGENTA WINS!"))
				return

			self.green += 1
			self.turn = MAGENTA
			self.graphics.draw_message(_("Next Turn: Magenta. Counter: ") + str(self.magenta), _)
			if self.pre_check_for_endgame():
				self.end = True
				self.graphics.draw_message(_("GREEN WINS!"), _)
				return

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
		print("post check for end: g ", self.green, " s? ", self.check_if_green_stays(), " m ", self.magenta, " ms? ", self.check_if_magenta_stays() )
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
