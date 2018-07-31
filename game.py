import Color
import TetrisConstants

class TetrisGame:
	def __init__(self):
		self.close_requested = False
		self.target_fps = 60
		self.window_size = (800, 600)
		self.title = "Tetris"
	def start(self):
		# Init
		self.screen = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption(self.title)
		self.clock = pygame.time.Clock()
		# Main Game Loop
		while not self.close_requested:
			# Handles "X" button of window
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.close_requested = True
			# Draws the game
			self.screen.fill(Color.WHITE)
			
			#pygame.draw.rect(self.screen, Color.BLACK, [x, y, width, height], 0)
			
			pygame.display.flip()
			self.clock.tick(self.target_fps)
			



import pygame
pygame.init()
game = TetrisGame()
game.start()
pygame.quit()


