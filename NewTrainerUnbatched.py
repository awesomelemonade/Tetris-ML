import numpy as np
from TetrisBoard import TetrisBoard
from TetrisConstants import *
from Color import Color
import time
import signal
import sys

import pickle
from collections import deque

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class AbstractModel:
	def __init__(self):
		self.conv1 = nn.Conv2d(1, 5, (2, 2), stride=2, padding=0)
		self.conv2 = nn.Conv2d(5, 10, (2, 2), stride=1, padding=0)
		self.dense1 = nn.Linear(360, 300)
		self.dense2 = nn.Linear(300, 300)
		self.dense3 = nn.Linear(300, 5)
		self.layers = (self.conv1, self.conv2, self.dense1, self.dense2, self.dense3)
		self.tensors = []
		for layer in self.layers:
			for name, parameter in layer.named_parameters():
				if parameter.requires_grad:
					self.tensors.append(parameter)
		self.weights = [parameter.numpy for parameter in self.tensors]
	def policyForward(self, data):
		data = torch.Tensor(data)
		x = self.conv1(data)
		x = self.conv2(x)
		x = F.relu(self.dense1(x.reshape(x.shape[0], -1)))
		x = F.relu(self.dense2(x))
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
				parameter.numpy = weight
class TetrisModel:
	def __init__(self):
		self.model = AbstractModel()
		self.model.load("weights.pkl")
		self.learningRate = 1e-6
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
		for i, board in boards:
			outNeurons = self.model.policyForward(self.preprocess(board)[np.newaxis, np.newaxis, :, :])
			softmax = nn.Softmax()
			probabilities = softmax(outNeurons)
			choice = torch.multinomial(probabilities, 1)[:, 0]
			loss_func = nn.CrossEntropyLoss()
			loss = loss_func(outNeurons, choice)
			loss.backward()
			self.derivatives.append(self.model.getDerivatives())
			if not board in self.rewardMap:
				self.rewardMap[board] = []
			self.rewardMap[board].append(len(self.rewards))
			self.rewards.append(0)
			for t in self.model.tensors:
				t = 0
			executor(board, choice)
	def gradientDescent(self):
		# Calculate Rewards TODO
		tempMap = {}
		for key in self.rewardMap.keys(): # Loops through all boards
			temp = len(self.rewardMap[key])
			tempMap[key] = len(self.rewardMap[key])
		average = sum(tempMap.values()) / len(tempMap.values())
		if len(self.runningAverage) == 0 or average > sum(self.runningAverage) / len(self.runningAverage):
			self.runningAverage.append(average)
		while len(self.runningAverage) > 3:
			self.runningAverage.popleft()
		adjust = sum(self.runningAverage) / len(self.runningAverage)
		print("#{}: {} - {} - {}".format(self.counter, list(tempMap.values()), average, adjust))
		for key in tempMap.keys():
			tempMap[key] = (tempMap[key] - adjust)
		self.counter += 1
		for key in self.rewardMap.keys():
			for value in self.rewardMap[key]:
				self.rewards[value] = tempMap[key]

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
			boards = [TetrisBoard(10, 20, seed=0) for x in range(50)]
			done = np.zeros(len(boards))
			while not np.all(done):
				self.env.step(boards, done, self.execute)
				for j, board in enumerate(boards):
					if done[j]:
						continue
					if not board.update():
						done[j] = True
					if j == 0:
						self.screen.fill(Color.WHITE)
						board.render(self.screen, *self.window_size)
						pygame.display.flip()
			self.env.gradientDescent()
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
		self.env.model.save("weights.pkl")
		sys.exit(0)



import pygame
pygame.init()
trainer = NewTrainer()
trainer.start()
pygame.quit()
