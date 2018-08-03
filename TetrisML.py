import numpy as np
import mygrad as mg
from mygrad.nnet.activations import softmax
from mygrad.nnet.losses import softmax_crossentropy
from TetrisConstants import *
import time

class AbstractModel:
	def __init__(self, layers):
		self.weights = []
		for i in range(len(layers) - 1):
			self.weights.append(mg.Tensor(np.random.randn(layers[i], layers[i + 1])))
	def policyForward(self, data):
		data = mg.Tensor(data)
		for i in range(len(self.weights) - 1):
			data = mg.matmul(data, self.weights[i]) # hidden layers
			data[data < 0] = 0 # ReLU
		return mg.matmul(data, self.weights[-1]) # outNeurons
	def getDerivatives(self):
		return [weight.grad for weight in self.weights]
	def gradientDescent(self, learning_rate, derivatives, rewards):
		# reward dimension = board id, turn #
		# derivative dimension = board id, turn #, weight #
		for boardDerivatives, boardRewards in zip(derivatives, rewards): # Loops through board id
			# boardDerivatives dimension = turn #, weight #, nparrays
			zipped = [np.moveaxis(np.array(weight), 0, -1) for weight in zip(*boardDerivatives)]
			# zipped dimension = weight #, turn #, nparrays
			boardRewards = np.array(boardRewards, dtype=np.float64)
			for weight, derivative, reward in zip(self.weights, zipped, boardRewards):
				weight -= np.sum(learning_rate * derivative * reward, axis=-1)
class TetrisModel:
	def __init__(self, size):
		self.size = size
		self.layers = [200, 50, 50, 5]
		self.model = AbstractModel(self.layers)
		self.learning_rate = 1e-4
		self.reset()
		self.cache = {}
		self.cache['arange'] = np.arange(self.layers[-1])
		self.cache['choice'] = []
		for i in range(self.layers[-1]):
			temp = np.zeros(self.layers[-1], dtype=int)
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
		grid = grid.astype(int) # Convert Boolean to Integer
		# Process Falling Piece
		for x in range(TetrisConstants.TEMPLATE_WIDTH):
			for y in range(TetrisConstants.TEMPLATE_HEIGHT):
				if not tetrisBoard.getTemplate(tetrisBoard.fallingPiece, x, y) == BLANK:
					grid[tetrisBoard.fallingPiece.x + x, tetrisBoard.fallingPiece.y + y] = -1
		# Process Next Piece TODO
		return grid.ravel() # Flatten
	def step(self, tetrisBoards, executor): # calculates and stores derivatives
		for i, tetrisBoard in enumerate(tetrisBoards):
			#temp = time.time()
			data = self.preprocess(tetrisBoard)
			#print("Preprocess: {}".format(time.time() - temp))
			#temp = time.time()
			outNeurons = self.model.policyForward(data)
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
	def evaluate(self, tetrisBoards): # calculates rewards
		for i, tetrisBoard in enumerate(tetrisBoards):
			for j in range(len(self.derivatives[i])):
				self.rewards[i].append(0)
	def gradientDescent(self):
		self.model.gradientDescent(self.learning_rate, self.derivatives, self.rewards)
	'''
	def policyForward(self, data):
		data = mg.Tensor(data.astype(int)) # Convert to Tensor
		hiddenNeurons = mg.matmul(data, self.model['W1']) # Matrix multiply weights #1
		hiddenNeurons[hiddenNeurons < 0] = 0 # ReLU
		outNeurons = mg.matmul(hiddenNeurons, self.model['W2']) # Matrix multiply weights #2
		return outNeurons
	def getDerivatives(self): # Extracts derivatives from backprop
		return (self.model['W1'].grad, self.model['W2'].grad)
	def gradientDescent(self): # rewards are delta score
		rewards = np.array(self.rewards, dtype=np.float64)
		# derivatives = list of list
		dW1, dW2 = zip(*self.derivatives)
		dW1 = np.moveaxis(np.array(dW1), 0, -1)
		dW2 = np.moveaxis(np.array(dW2), 0, -1)
		rewards[-1] = - 1 / len(rewards) # discourage all steps slightly because we lost
		rewards = np.cumsum(rewards[::-1])[::-1]
		self.model['W1'] += np.sum(self.learning_rate * dW1 * rewards, axis=-1)
		self.model['W2'] += np.sum(self.learning_rate * dW2 * rewards, axis=-1)
		self.reset()
	'''
