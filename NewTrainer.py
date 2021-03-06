import numpy as np
from TetrisBoard import TetrisBoard
from TetrisConstants import *
from Color import Color
import time
import signal
import sys

import mygrad as mg
from mygrad.nnet.activations import softmax
from mygrad.nnet.losses import softmax_crossentropy
from mynn.layers.conv import conv
from mynn.layers.dense import dense
from mygrad.nnet.layers import max_pool
from mynn.initializers.glorot_uniform import glorot_uniform
from mynn.activations.relu import relu

class AbstractModel:
	def __init__(self):
		self.conv1 = conv(1, 5, 2, 2, stride=2, padding=0, weight_initializer=glorot_uniform)
		self.conv2 = conv(5, 10, 2, 2, stride=1, padding=0, weight_initializer=glorot_uniform)
		self.dense1 = dense(360, 300, weight_initializer=glorot_uniform)
		self.dense2 = dense(300, 300, weight_initializer=glorot_uniform)
		self.dense3 = dense(300, 5, weight_initializer=glorot_uniform)
		self.layers = (self.conv1, self.conv2, self.dense1, self.dense2, self.dense3)
		self.tensors = []
		for layer in self.layers:
			for parameter in layer.parameters:
				self.tensors.append(parameter)
		self.weights = [parameter.data for parameter in self.tensors]
	def policyForward(self, data):
		data = mg.Tensor(data)
		x = self.conv1(data)
		x = self.conv2(x)
		x = relu(self.dense1(x.reshape(x.shape[0], -1)))
		x = relu(self.dense2(x))
		return self.dense3(x)
	def getDerivatives(self):
		return [parameter.grad for parameter in self.tensors]
	def gradientDescent(self, learningRate, derivatives, rewards):
		for derivative, reward in zip(derivatives, rewards):
			for weight, grad in zip(self.weights, derivatives):
				weight -= learningRate * grad * reward
	def save(self, filename):
		with open(filename, mode="wb") as opened_file:
			pickle.dump(self.weights, opened_file)
class TetrisModel:
	def __init__(self):
		self.model = AbstractModel()
		self.learningRate = 1e-4
		self.reset()
	def reset(self):
		self.derivatives = []
		self.rewards = []
	def preprocess(self, tetrisBoard):
		# Process Board
		grid = tetrisBoard.grid != BLANK
		grid = grid.astype(np.float64)
		# Process Falling Piece
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not tetrisBoard.getTemplate(tetrisBoard.fallingPiece, x, y) == BLANK:
					grid[tetrisBoard.fallingPiece.x + x, tetrisBoard.fallingPiece.y + y] = -1
		# Process Next Piece TODO
		return grid
	def convert(self, derivatives):
		ret = []
		print(derivatives[0].shape)
		for batch in range(len(derivatives[0])):
			temp = []
			for i in range(len(derivatives)):
				temp.append(derivatives[i][batch, :])
			ret.append(temp)
		return ret
	def sample(self, probabilities):
		choices = []
		for i in range(probabilities.shape[0]):
			choices.append(np.random.choice(probabilities.shape[1], p=probabilities[i, :]))
		return np.array(choices)
	def step(self, tetrisBoards, done, executor):
		boards = [(i, board) for i, board in enumerate(tetrisBoards) if not done[i]]
		stacked = np.stack([self.preprocess(board) for i, board in boards])[:, np.newaxis, :, :]
		outNeurons = self.model.policyForward(stacked)
		probabilities = softmax(outNeurons)
		choices = self.sample(probabilities.data)
		assert len(choices) == len(boards)
		loss = softmax_crossentropy(outNeurons, choices)
		loss.backward()
		# Store gradients
		converted = self.convert(self.model.getDerivatives())
		print(len(converted))
		self.derivatives.extend(converted) # Derivatives are batched
		self.rewards.append([1 if choice == 0 else 0 for choice in choices])
		print(len(self.model.getDerivatives()))
		print(len(self.rewards[-1]))
		assert len(self.derivatives[-1]) == len(self.rewards[-1])
		# Calculate rewards array
		loss_null_gradients()
		for choice, i, board in zip(choices, *boards):
			executor(board, choice)
	def gradientDescent(self):
		# Calculate Rewards TODO
		self.model.gradientDescent(self.learningRate, self.derivatives, self.rewards)
		self.reset()
class NewTrainer:
	def start(self):
		self.BLOCK_SIZE = 40
		self.window_size = (3 * 10 * self.BLOCK_SIZE, 1 * 20 * self.BLOCK_SIZE)
		self.screen = pygame.display.set_mode(self.window_size)
		pygame.display.set_caption("Tetris Trainer")
		signal.signal(signal.SIGINT, self.signalHandler)
		self.env = TetrisModel()
		while True:
			boards = [TetrisBoard(10, 20, seed=0) for x in range(20)]
			done = np.zeros(len(boards))
			while not np.all(done):
				self.env.step(boards, done, self.execute)
				for i, board in enumerate(boards):
					if done[j]:
						continue
					if not board.update():
						done[j] = True
					if j == 0:
						self.screen.fill(Color.WHITE)
						board.render(self.screen, *self.window_Size)
						pygame.display.flip()
			self.env.gradientDescent()
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
	def signalHandler(self, sig, frame):
		self.env.model.save("weights.pkl")
		sys.exit(0)



import pygame
pygame.init()
trainer = NewTrainer()
trainer.start()
pygame.quit()
