from Color import Color
from TetrisBoard import TetrisBoard
import time

class TetrisGame:
	def __init__(self):
		self.close_requested = False
		self.target_fps = 60
		self.window_size = (10 * 40, 20 * 40)
		self.title = "Tetris"
	def start(self):
		# Init
		self.screen = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption(self.title)
		self.clock = pygame.time.Clock()
		board = TetrisBoard(10, 20, *self.window_size, seed=0)
		lastUpdate = time.time()
		UPDATE_INTERVAL = 1
		# Main Game Loop
		while not self.close_requested:
			# Handles "X" button of window
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.close_requested = True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_w:
						board.rotateFallingPiece(1)
					if event.key == pygame.K_a:
						board.moveFallingPiece(moveX=-1, moveY=0)
					if event.key == pygame.K_d:
						board.moveFallingPiece(moveX=1, moveY=0)
					if event.key == pygame.K_s:
						board.moveFallingPiece(moveX=0, moveY=1)
					if event.key == pygame.K_SPACE:
						board.spike()
						board.update()
			# Updates the game
			if lastUpdate + UPDATE_INTERVAL < time.time():
				board.update()
				lastUpdate += UPDATE_INTERVAL
			# Draws the game
			self.screen.fill(Color.BLACK)
			board.render(self.screen, *self.window_size)
			#pygame.draw.rect(self.screen, Color.BLACK, [x, y, width, height], 0)

			pygame.display.flip()
			self.clock.tick(self.target_fps)



import pygame
pygame.init()
game = TetrisGame()
game.start()
pygame.quit()
