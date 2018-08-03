import numpy as np
import mygrad as mg
from mygrad.nnet.activations import softmax
from mygrad.nnet.losses import softmax_crossentropy
from TetrisConstants import *
import time
import pickle
from collections import deque
from itertools import zip_longest
from mynn.layers.conv import conv
from mynn.layers.dense import dense
from mygrad.nnet.layers import max_pool
from mynn.initializers.glorot_uniform import glorot_uniform
from mynn.activations.relu import relu
from mynn.optimizers.sgd import SGD

class AbstractModel:
	def __init__(self):
		self.conv1 = conv(1, 5, 2, 2, stride=2, padding=0, weight_initializer=glorot_uniform)
		self.conv2 = conv(5, 10, 2, 2, stride=1, padding=0, weight_initializer=glorot_uniform)
		self.dense1 = dense(240, 300, weight_initializer=glorot_uniform) # 9 * 19 = 171
		self.dense2 = dense(300, 300, weight_initializer=glorot_uniform)
		self.dense3 = dense(300, 5, weight_initializer=glorot_uniform)
		self.layers = (self.conv1, self.conv2, self.dense1, self.dense2, self.dense3)
		self.tensors = []
		for layer in self.layers:
			for parameter in layer.parameters:
				self.tensors.append(parameter)
		self.weights = [parameter.data for parameter in self.tensors]
	def policyForward(self, data):
		data = mg.Tensor(data[np.newaxis, np.newaxis])
		x = self.conv1(data)
		x = max_pool(x, (2, 2), 1)
		x = self.conv2(x)
		x = relu(self.dense1(x.reshape(x.shape[0], -1)))
		x = relu(self.dense2(x))
		return self.dense3(x)
	def getDerivatives(self):
		return [parameter.grad for parameter in self.tensors]
	def gradientDescent(self, learning_rate, derivatives, rewards):
		for boardDerivatives, boardRewards in zip(derivatives, rewards):
			zipped = [np.moveaxis(np.array(weight), 0, -1) for weight in zip(*boardDerivatives)]
			boardRewards = np.array(boardRewards, dtype=np.float64)
			for weight, derivative, reward in zip(self.weights, zipped, boardRewards):
				weight -= np.sum(learning_rate * derivative * reward, axis=-1)
	def save(self, filename):
		with open(filename, mode="wb") as opened_file:
			pickle.dump(self.weights, opened_file)
class TetrisModel:
	def __init__(self, size):
		self.model = AbstractModel()
		self.averageTurns = deque()
		self.size = size
		self.learning_rate = 1e-4
		self.reset()
		self.cache = {}
		self.cache['arange'] = np.arange(5)
		self.cache['choice'] = []
		for i in range(5):
			temp = np.zeros(5, dtype=int)
			temp[i] = 1
			self.cache['choice'].append(temp)
	def reset(self):
		self.derivatives = []
		self.rewards = []
		for i in range(self.size):
			self.derivatives.append([])
			self.rewards.append([])
	def preprocess(self, tetrisBoard): # Preprocesses the tetris board to a flattened numpy array
		# Process Board
		grid = tetrisBoard.grid != BLANK # Grid of 0's and 1's
		grid = grid.astype(np.float64) # Convert Boolean to Integer
		# Process Falling Piece
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not tetrisBoard.getTemplate(tetrisBoard.fallingPiece, x, y) == BLANK:
					grid[tetrisBoard.fallingPiece.x + x, tetrisBoard.fallingPiece.y + y] = -1
		# Process Next Piece TODO
		return grid
	def step(self, tetrisBoards, executor, done): # calculates and stores derivatives
		for i, tetrisBoard in enumerate(tetrisBoards):
			if done[i]:
				continue
			#temp = time.time()
			data = self.preprocess(tetrisBoard)
			#print("Preprocess: {}".format(time.time() - temp))
			#temp = time.time()
			outNeurons = self.model.policyForward(data)
			outNeurons = outNeurons.reshape(5)
			probabilities = softmax(outNeurons)
			#print("Forward: {}".format(time.time() - temp))
			#temp = time.time()
			choice = np.random.choice(self.cache['arange'], p=probabilities)
			reward = self.cache['choice'][choice]
			#print("Choice: {}".format(time.time() - temp))
			#temp = time.time()
			loss = softmax_crossentropy(outNeurons.reshape(1, len(outNeurons)), reward)
			loss.backward()
			#print("Backprop: {}".format(time.time() - temp))
			#temp = time.time()
			self.derivatives[i].append(self.model.getDerivatives())
			loss.null_gradients()
			#print("Store: {}".format(time.time() - temp))
			executor(tetrisBoard, choice)
	def evaluate(self, tetrisBoards, done): # calculates rewards
		for i, tetrisBoard in enumerate(tetrisBoards):
			if done[i]:
				continue
			self.rewards[i].append(tetrisBoard.lowestBlankLine())
	'''def gradientDescent(self):
		# board #, turn # -> turn #, board #
		swapped = [[i for i in element if i is not None] for element in list(zip_longest(*self.rewards))]
		# Average
		for i in range(len(swapped)):
			swapped[i] = sum(swapped[i]) / len(swapped[i]) - 0.1 # Average height
		for board in self.rewards:
			for i in range(len(board)):
				board[i] -= swapped[i]
				board[i] = -board[i]
		
		averageTurns = sum([len(derivative) for derivative in self.derivatives]) / len(self.derivatives)
		print("Average Turns: {}".format(averageTurns))
		self.model.gradientDescent(self.learning_rate, self.derivatives, self.rewards)
		self.reset()
	'''
	
	def gradientDescent(self):
		averageTurns = sum([len(derivative) for derivative in self.derivatives]) / len(self.derivatives)
		self.averageTurns.append(averageTurns)
		runningAverage = sum(self.averageTurns) / len(self.averageTurns)
		# Remove excess
		while len(self.averageTurns) > 20:
			self.averageTurns.popleft()
		
		calculated = [(len(reward) - (runningAverage - 2)) ** 2 for reward in self.rewards] # Square the loss to be more drastic!
		for i, reward in enumerate(calculated): # Loops through boards
			for j in range(len(self.rewards[i])):
				self.rewards[i][j] = reward
		print("Average Turns: {} - {}".format(averageTurns, runningAverage))
		self.model.gradientDescent(self.learning_rate, self.derivatives, self.rewards)
		self.reset()
	
