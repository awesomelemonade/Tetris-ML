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
import pickle
from collections import deque

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
			for weight, grad in zip(self.weights, derivative):
				weight -= learningRate * grad * reward
	def save(self, filename):
		with open(filename, mode="wb") as opened_file:
			pickle.dump(self.weights, opened_file)
	def load(self, filename):
		with open(filename, mode="rb") as opened_file:
			weights = pickle.load(opened_file)
			for weight, parameter in zip(weights, self.tensors):
				parameter.data = weight
class TetrisModel:
	def __init__(self):
		self.model = AbstractModel()
		self.model.load("weights.pkl")
		self.learningRate = 1e-7
		self.counter = 0
		self.runningAverage = deque()
		self.reset()
	def reset(self):
		self.derivatives = []
		self.rewards = []
		self.rewardMap = {}
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
	def sample(self, probabilities):
		choices = []
		for i in range(probabilities.shape[0]):
			choices.append(np.random.choice(probabilities.shape[1], p=probabilities[i, :]))
		return np.array(choices)
	def step(self, tetrisBoards, done, executor):
		boards = [(i, board) for i, board in enumerate(tetrisBoards) if not done[i]]
		for i, board in boards:
			outNeurons = self.model.policyForward(self.preprocess(board)[np.newaxis, np.newaxis, :, :])
			probabilities = softmax(outNeurons)
			choice = np.random.choice(5, p=probabilities.reshape(5))
			loss = softmax_crossentropy(outNeurons, np.array([choice]))
			loss.backward()
			self.derivatives.append(self.model.getDerivatives())
			if not board in self.rewardMap:
				self.rewardMap[board] = []
			self.rewardMap[board].append(len(self.rewards))
			self.rewards.append(None) # Temp placeholder
			loss.null_gradients()
			executor(board, choice)
	def evaluate(self, tetrisBoard, reward):
		self.rewards[self.rewardMap[tetrisBoard][-1]] = reward
	def gradientDescent(self):
		# Print Info
		gameLengths = [len(self.rewardMap[board]) for board in self.rewardMap.keys()]
		average = sum(gameLengths) / len(gameLengths)
		print("#{}: {} - {}".format(self.counter, gameLengths, average))
		self.counter += 1
		# Calculate Rewards
		self.calculateRewards(self.rewardMap, self.rewards, 0.99)
		# Gradient Descent
		self.model.gradientDescent(self.learningRate, self.derivatives, self.rewards)
		self.reset()
	def calculateRewards(self, rewardMap, rewards, discount):
		for board in rewardMap.keys():
			indices = rewardMap[board]
			discounts = discount ** np.arange(len(indices))
			discounts = discounts[::-1] # Reverses Discounts
			newRewards = np.zeros(len(indices))
			for i in range(len(indices)):
				if rewards[indices[i]] != 0:
					additions = rewards[indices[i]] * discounts[len(discounts) - i - 1:]
					newRewards += np.pad(additions, (0, len(newRewards) - len(additions)), 'constant', constant_values=(0, 0))
			# Actually put the newRewards into the giant rewards list
			for index, reward in zip(indices, newRewards):
				rewards[index] = reward
from datetime import datetime
import os
class NewTrainer:
	def start(self):
		self.BLOCK_SIZE = 40
		self.window_size = (3 * 10 * self.BLOCK_SIZE, 1 * 20 * self.BLOCK_SIZE)
		if RENDER:
			self.screen = pygame.display.set_mode(self.window_size)
			pygame.display.set_caption("Tetris Trainer")
		signal.signal(signal.SIGINT, self.signalHandler)
		self.env = TetrisModel()
		iteration = 0
		while True:
			boards = [TetrisBoard(10, 20, seed=0) for x in range(20)]
			done = np.zeros(len(boards))
			while not np.all(done):
				self.env.step(boards, done, self.execute)
				for j, board in enumerate(boards):
					if done[j]:
						continue
					prevHeight = board.lowestBlankLine()
					status = board.update()
					newHeight = board.lowestBlankLine()
					if status == 1: # If a piece was placed
						if newHeight == prevHeight: # Didn't increase the weight!
							self.env.evaluate(board, 10) # Arbitrary Weight
						else:
							self.env.evaluate(board, (newHeight - prevHeight - 0.5) * 10) # Reward Function
					else:
						self.env.evaluate(board, 0)
					if status == -1: # Lose Condition
						done[j] = True
					if RENDER and j == 0:
						self.screen.fill(Color.WHITE)
						board.render(self.screen, *self.window_size)
						pygame.display.flip()
			self.env.gradientDescent()
			if (iteration % 10) == 0:
				if not os.path.exists("./checkpoints/"):
					os.makedirs("./checkpoints/")
				self.env.model.save(datetime.now().strftime("./checkpoints/w-ckpt-i"+str(iteration)+"-%m-%d--%H-%M-%S.pkl"))
			iteration+=1
	def execute(self, board, action):
		if action == 0:
			board.rotateFallingPiece(1)
		if action == 1:
			board.rotateFallingPiece(-1)
		if action == 2:
			board.moveFallingPiece(moveX=-1, moveY=0)
		if action == 3:
			board.moveFallingPiece(moveX=1, moveY=0)
		if action == 4:
			pass # do nothing
	def signalHandler(self, sig, frame):
		print("Sigkill Received: Saving")
		self.env.model.save("weights.pkl")
		sys.exit(0)

RENDER = True

if RENDER:
	import pygame
	pygame.init()
trainer = NewTrainer()
trainer.start()
if RENDER:
	pygame.quit()
