from Color import Color
from TetrisBoard import TetrisBoard
import time

class TetrisGame:
	def __init__(self):
		self.close_requested = False
		self.target_fps = 60
		self.window_size = (30 * 40, 20 * 40)
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
			playing = True
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.close_requested = True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_UP:
						board.rotateFallingPiece(1)
					if event.key == pygame.K_LEFT:
						board.moveFallingPiece(moveX=-1, moveY=0)
					if event.key == pygame.K_RIGHT:
						board.moveFallingPiece(moveX=1, moveY=0)
					if event.key == pygame.K_DOWN:
						board.moveFallingPiece(moveX=0, moveY=1)
					if event.key == pygame.K_SPACE:
						board.spike()
						board.update()
			# Updates the game
			lose = False
			if lastUpdate + UPDATE_INTERVAL < time.time():
				if(not board.update()):
					lose = True
				else:
					lastUpdate += UPDATE_INTERVAL
			# Check for lose
			if lose:
				board.lose(self.screen, self.window_size)
			else:
				#Draw the Board
				self.screen.fill((255,239,213))
				board.render(self.screen, * self.window_size, shiftx = self.window_size[0]/3)
				board.showScore(self.screen, self.window_size)
				board.showLevel(self.screen, self.window_size)
				#levelcheck
				if(board.linesCleared >= board.level * 10):
					board.level += 1
			#pygame.draw.rect(self.screen, Color.BLACK, [x, y, width, height], 0)

			pygame.display.flip()
			self.clock.tick(self.target_fps)



import pygame
pygame.init()
game = TetrisGame()
game.start()
pygame.quit()
