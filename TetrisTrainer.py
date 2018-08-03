import numpy as np
from TetrisBoard import TetrisBoard
from TetrisML import *
from Color import Color
import time
class TetrisTrainer:
	def start(self):
		numBoards = 20
		env = TetrisModel(numBoards)
		self.BLOCK_SIZE = 40
		self.window_size = (3 * 10 * self.BLOCK_SIZE, 1 * 20 * self.BLOCK_SIZE)
		self.screen = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption("Tetris Trainer")
		self.clock = pygame.time.Clock()
		for i in range(100):
			boards = [TetrisBoard(10, 20, seed=0) for j in range(numBoards)]
			done = np.zeros(len(boards))
			while not np.all(done):
				temp = time.time()
				env.step(boards, self.execute, done)
				for j, board in enumerate(boards):
					if done[j]:
						continue
					if not board.update():
						done[j] = True
					if j == 0:
						self.screen.fill(Color.WHITE)
						board.render(self.screen, *self.window_size)
						pygame.display.flip()
				env.evaluate(boards, done)
			env.gradientDescent()
		env.model.save("weights.pkl")
	def execute(self, board, action):
		if action == 0:
			board.rotateFallingPiece(1)
		if action == 1:
			board.moveFallingPiece(moveX=-1, moveY=0)
		if action == 2:
			board.moveFallingPiece(moveX=1, moveY=0)
		if action == 3:
			board.moveFallingPiece(moveX=0, moveY=1)
		if action == 4:
			pass # do nothing

import pygame
pygame.init()
trainer = TetrisTrainer()
trainer.start()
pygame.quit()
