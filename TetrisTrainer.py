import numpy as np
from TetrisBoard import TetrisBoard
from TetrisML import TetrisML
from Color import Color
class TetrisTrainer:
	def start(self):
		env = TetrisML()
		self.BLOCK_SIZE = 40
		self.window_size = (3 * 10 * self.BLOCK_SIZE, 1 * 20 * self.BLOCK_SIZE)
		self.screen = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption("Tetris Trainer")
		self.clock = pygame.time.Clock()
		for i in range(100):
			#print(np.sum(env.model.model['W1'].data))
			board = TetrisBoard(10, 20, seed=0)
			while True:
				action = env.step(board)
				if action == 0:
					board.rotateFallingPiece(1)
				if action == 1:
					board.moveFallingPiece(moveX=-1, moveY=0)
				if action == 2:
					board.moveFallingPiece(moveX=1, moveY=0)
				if action == 3:
					board.moveFallingPiece(moveX=0, moveY=1)
				# Action #4 does nothing
				if not board.update():
					env.gameover()
					break
				self.screen.fill(Color.WHITE)
				board.render(self.screen, *self.window_size)
				pygame.display.flip()
				self.clock.tick(60)
			print("Score: {}".format(board.score))


import pygame
pygame.init()
trainer = TetrisTrainer()
trainer.start()
pygame.quit()
