from Color import Color
from TetrisBoard import TetrisBoard

class TetrisGame:
	def __init__(self):
		self.close_requested = False
		self.target_fps = 3
		self.window_size = (10 * 40, 20 * 40)
		self.title = "Tetris"
	def start(self):
		# Init
		self.screen = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption(self.title)
		self.clock = pygame.time.Clock()
		board = TetrisBoard(10, 20, *self.window_size, seed=0)
		# Main Game Loop
		while not self.close_requested:
			# Handles "X" button of window
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.close_requested = True
			# Draws the game
			self.screen.fill(Color.BLACK)
			
			board.update()
			board.render(self.screen, *self.window_size)
			#pygame.draw.rect(self.screen, Color.BLACK, [x, y, width, height], 0)
			
			pygame.display.flip()
			self.clock.tick(self.target_fps)
			


import pygame
pygame.init()
game = TetrisGame()
game.start()
pygame.quit()


