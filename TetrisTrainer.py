import numpy as np
from TetrisBoard import TetrisBoard
from TetrisML import TetrisML
class TetrisTrainer:
	def __init__(self, numBoards):
		self.boards = []
		for i in range(numBoards):
			self.boards.append(TetrisBoard(10, 20, seed=i))
	def start(self):
		done = np.zeros(len(self.boards))
		env = TetrisML()
		while not np.all(done):
			env.step(self.boards)
			for i, board in enumerate(self.boards):
				if not board.update():
					done[i] = True

trainer = TetrisTrainer(10)
trainer.start()
